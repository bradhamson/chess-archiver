import json
import datetime

from abc import ABC, abstractmethod
from typing import Dict, List, Union, Generator

import requests

from . game import Game, Player

class Service(ABC):
    
    @abstractmethod
    @property
    def base_url(self) -> str:
        '''API base url for a service.
        '''
        pass

    @abstractmethod
    @property
    def user_name(self) -> str:
        '''Username of the service subscriber/target.
        '''
        pass

    @abstractmethod
    def games(self) -> Generator[Game, None, None]:
        '''Composes and invokes a call to the service's api requesting all game data for user.
        Parses response and converts data into instances of Game.

        Returns:
            Generator[Game, None, None]: Generator that yields Game instances built from each game 
                parsed from response data.

        Raises:
            HTTPError: if response code != 200.
        '''
        pass


class ChessService(Service):

    def __init__(self) -> None:
        self._base_url = ''
        self._user_name = ''

    @property
    def base_url(self) -> str:
        return self._base_url
    
    @property
    def user_name(self) -> str:
        return self._user_name
    
    def _get_date_for_request(self) -> Dict[str, str]:
        '''Intended for use when running cron job on a montly basis. Assumes today is
        within the targeted month.

            Returns:
                Dict[str, str]: Today's year and month accessible by dict key in a string format.
        '''
        today = datetime.datetime.now()
        year = ''
        month = ''
        return {'year': year, 'month': month}
    
    def _build_player(self, player_data: Dict[str, Union[str, int]]) -> Player:
        '''Handles extracted Player data from JSON repsonse and builds an instance of Player

            Args:
                player_data (Dict[str, str | int]): Player data extracted from JSON response.

            Returns:
                Player: Instance of Player built from parsed Player data extracted from JSON response.
        '''
        player = Player(
            player_id=player_data['uuid'],
            user_name=player_data['username'],
            rating=player_data['rating'],
            result=player_data['result']
        )
        return player
    
    def _generate_game(self, resp: requests.Response) -> Generator[Game, None, None]:
        '''Handles extracting data from JSON response and generating instances of Game.

            Args:
                resp (requests.Response): Response from GET request to service's API containing game and
                    player data.

            Returns:
                Generator[Game, None, None]: Generator that yields Game instances built from each game 
                    parsed from response data.
        '''
        content = json.loads(resp.json)
        games_response = content['games']
        for game_data in games_response:
            game_id = game_data['uuid']
            game = Game(
                game_id=game_id,
                url=f'https://chess.com/game/live/{game_id}',
                pgn_data=game_data['pgn'],
                white=self._build_player(game_data['white']),
                black=self._build_player(game_data['black']),
                time_control=game_data['time_class'],
                length_ms=int(game_data['time_control'])
            )
            yield game


    def games(self) -> Generator[Game, None, None]:
        request_date = self._get_date_for_request()
        request_url = f'{self.base_url}/{self.user_name}/games/{request_date["year"]}/{request_date["month"]}/'
        resp = requests.get(request_url)
        games = self._generate_game(resp=resp)
        return games


class LichessService(Service):
    
    def __init__(self) -> None:
        self._base_url = ''
        self._user_name = ''

    @property
    def base_url(self) -> str:
        return self._base_url
    
    @property
    def user_name(self) -> str:
        return self._user_name
    
    def _build_player(self, player_data) -> Player:
        pass

    def _build_game(self, resp: requests.Response) -> Game:
        pass

    def games(self) -> Generator[Game, None, None]:
        pass


class ProxyService(Service):
    def __init__(self, platform_service: Union[ChessService, LichessService]) -> None:
        self._platform_service = platform_service

    @property
    def platform_service(self) -> Service:
        return self._platform_service
    
    @platform_service.setter
    def platform_service(self, service: Service) -> None:
        self._platform_service = service

    @property
    def base_url(self) -> str:
        return self.platform_service.base_url
    
    @property
    def user_name(self) -> str:
        return self.platform_service.user_name

    def games(self, format: str) -> Generator[Game, None, None]:
        return self.platform_service.games()