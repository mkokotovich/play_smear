import { Cookie } from 'ng2-cookies/ng2-cookies';
import { Injectable } from '@angular/core';
import { Router } from '@angular/router';

import { AuthInfo } from './model/auth-info';
import { AuthResults } from './model/auth-results';
import { Player } from './model/player';
import { PlayerStats } from './model/player-stats';
import { GameId } from './model/game-id';
import { GameAndUser } from './model/game-and-user';
import { GameCreateInput } from './model/game-create-input';
import { GameJoinResults } from './model/game-join-results';
import { GameStartStatus } from './model/game-start-status';
import { HandService } from './hand.service';
import { SmearApiService } from './smear-api.service';

@Injectable()
export class GameService {

    public gameCreateInput = new GameCreateInput(0, 0, 0, 0);
    public gameAndUser = new GameAndUser("", "");
    public authInfo = new AuthInfo("");
    public playerStats: PlayerStats;
    public welcomeMessage = "";
    public errorMessage = "";
    public disableCreateButton = false;
    public disableJoinButton = false;
    public pointsToPlayTo: number = 11;
    public numTeams: number = 0;
    public playersAwaitingTeams: string[] = new Array<string>();
    public teamMembers: string[][] = new Array<Array<string>>();
    private numPlayers: number;
    private players: Player[];
    public playersSoFar: string[] = new Array<string>();
    private username: string;
    private gameId: GameId = new GameId("");
    public userEmail: string;
    public authButtonString: string = "Sign in";
    public loggedIn: Boolean = false;
    public disableAuthButton: Boolean = false;
    private cancellingGame: Boolean = false;
    public gameIsActive: Boolean = false;

    constructor(private router: Router,
                public handService: HandService,
                public smearApiService: SmearApiService) { }

    resetGame() {
        this.cancellingGame = true;
        this.gameIsActive = false;
        this.pointsToPlayTo = 11;
        this.numTeams = 0;
        this.teamMembers = new Array<Array<string>>();
        this.playersAwaitingTeams = new Array<string>();
        this.numPlayers = 0;
        this.players = new Array<Player>();
        this.playersSoFar = new Array<string>();
        this.gameAndUser.game_id = "";
        this.gameId.game_id = "";
        this.welcomeMessage = "";
        this.errorMessage = "";
        this.disableCreateButton = false;
        this.disableJoinButton = false;
        this.disableAuthButton = false;
        this.handService.resetHand();
    }

    loginUserFromCookie() {
        if (!this.loggedIn) {
            this.userEmail = Cookie.get("user_email");
            if (this.userEmail && this.userEmail.length != 0) {
                this.loginUserWithEmail(this.userEmail);
            }
        }
    }

    loginUserWithEmail(email:string) {
        this.authInfo.email = email;
        Cookie.set("user_email", email);
        this.disableAuthButton = true;
        this.smearApiService.loginUser(this.authInfo)
          .subscribe(
            authResults => this.authReturned(authResults),
            err => this.handleStartError(err, "Unable to log in with the supplied email, try again later")
          );
    }

    logoutUser() {
        this.disableAuthButton = true;
        Cookie.delete("user_email");
        this.userEmail = "";
        this.smearApiService.logoutUser()
                            .subscribe( authResults => this.authReturned(authResults),
                                        err => this.handleStartError(err, "Unable to log out, try again later"));
    }

    authReturned(authResults:AuthResults) {
        this.disableAuthButton = false;
        if (authResults.success) {
            //TODO Save email to cookie
            if (this.loggedIn == false) {
                this.authButtonString = "Sign out";
                this.loggedIn = true;
            } else {
                this.authButtonString = "Sign in";
                this.loggedIn = false;
            }
        }
    }

    public authButtonClicked() {
        if (this.loggedIn == false) {
            // The user is now trying to log in
            this.loginUserWithEmail(this.userEmail)
        } else {
            this.logoutUser()
        }
    }

    public getUserStats() {
        if (this.loggedIn == false) {
            return;
        }
        this.smearApiService.getPlayerStats()
                            .subscribe( playerStats => this.playerStatsReturned(playerStats),
                                        err => this.handleStartError(err, "Unable to retrieve player stats"));
    }

    playerStatsReturned(playerStats: PlayerStats) {
        this.playerStats = playerStats;
    }

    manageGame() {
        this.router.navigate(['/play']);
        this.playersSoFar = new Array<string>();
        this.welcomeMessage = "";
        this.errorMessage = "";
        this.disableCreateButton = false;
        this.disableJoinButton = false;
        this.disableAuthButton = false;
        this.handService.startNewHand();
    }

    createAndJoinGame() {
        this.welcomeMessage = "Waiting for game to start...";
        this.errorMessage = "";
        this.disableCreateButton = true;
        // Send numPlayers to server to start a game, retreive a gameID?
        // Increment numHumanPlayers to account for self
        var numHumanPlayers = Number(this.gameCreateInput.numHumanPlayers) + 1
        this.gameCreateInput.numHumanPlayers = numHumanPlayers
        this.gameCreateInput.pointsToPlayTo = this.pointsToPlayTo;
        this.gameCreateInput.numTeams = this.numTeams;
        this.smearApiService.gameCreate(this.gameCreateInput)
                            .subscribe( gameId => this.gameIsCreated(gameId),
                                        err => this.handleStartError(err, "Unable to create game, make sure you have a valid number of players and try again"));

    }

    gameIsCreated(gameId: GameId) {
        this.gameIsActive = true;
        this.gameAndUser.game_id = gameId.game_id;
        this.welcomeMessage = "Game " + this.gameAndUser.game_id + " created successfully!";
        if (this.gameCreateInput.numHumanPlayers != 0) {
            this.welcomeMessage += " Tell the other players to use game id " + this.gameAndUser.game_id + " and join the game!";
        }
        this.joinGame();
    }

    rejoinGame() {
        this.gameAndUser.game_id = Cookie.get("game_id");
        this.gameAndUser.username = Cookie.get("username");
        if (this.gameAndUser.game_id == undefined || this.gameAndUser.game_id == "") {
            return this.unableToJoin("An existing game could not be found");
        }
        this.welcomeMessage = "Attempting to rejoin a previous game...";
        this.errorMessage = "";
        this.disableJoinButton = true;
        this.smearApiService.gameRejoin(this.gameAndUser)
                            .subscribe( gameJoinResults => this.checkGameStatus(gameJoinResults),
                                        err => this.unableToJoin(err));
    }

    unableToJoin(err: any) {
        this.welcomeMessage = "Unable to join any existing games, create or join a game to play";
        this.errorMessage = <any>err;
        this.disableJoinButton = false;
        this.gameIsActive = false;
        this.router.navigate(['/start']);
    }

    joinGame() {
        this.deleteGameCookies();
        this.welcomeMessage += "\nJoining game..."
        this.cancellingGame = false;
        this.errorMessage = "";
        this.disableJoinButton = true;
        this.smearApiService.gameJoin(this.gameAndUser)
                            .subscribe( gameJoinResults => this.checkGameStatus(gameJoinResults),
                                        err => this.handleStartError(err, "Unable to join game, try creating one or joining another game"));
        this.router.navigate(['/lobby']);
    }

    deleteGameCookies() {
        Cookie.delete("bid_submitted");
        Cookie.delete("game_id");
        Cookie.delete("hand_finished");
        Cookie.delete("hand_id");
        Cookie.delete("trump");
        Cookie.delete("username");
    }

    checkGameStatus(gameJoinResults: GameJoinResults) {
        if (this.cancellingGame) {
            this.cancellingGame = false;
            return;
        }
        this.gameIsActive = true;
        if (gameJoinResults) {
            this.setGameInfo(gameJoinResults.game_id,
                             gameJoinResults.username,
                             gameJoinResults.team_id,
                             gameJoinResults.num_teams,
                             gameJoinResults.points_to_play_to,
                             gameJoinResults.graph_prefix);
        }
        this.saveGameInfoInCookie();
        this.smearApiService.getGameStartStatus(this.gameAndUser)
                            .subscribe( gameStartStatus => this.gameIsReady(gameStartStatus),
                                        err => this.handleStartError(err, "Unable to join game, try creating one or joining another game"));
    }

    updatePlayersWaiting(playersSoFar: Array<string>) {
        for (var i = 0; i < playersSoFar.length; i++) {
            let player = playersSoFar[i];
            if (this.playersAwaitingTeams.indexOf(player) > -1) {
                continue;
            }
            let found = false;
            for (var j = 0; j < this.teamMembers.length; j++) {
                if (this.teamMembers[j].indexOf(player) > -1) {
                    found = true;
                    break;
                }
            }
            if (found) {
                continue;
            }
            // If not found yet, it must be a new player
            this.playersAwaitingTeams.push(player);
        }
    }

    gameIsReady(gameStartStatus: GameStartStatus) {
        if (this.cancellingGame) {
            this.cancellingGame = false;
            return;
        }
        this.playersSoFar = gameStartStatus.player_names;
        this.updatePlayersWaiting(gameStartStatus.player_names);
        if (gameStartStatus.ready == false) {
            // If we aren't ready, check again in two seconds
            setTimeout(function() {
                this.checkGameStatus(null);
            }.bind(this), 2000);
            return;
        }
        this.setPlayers(gameStartStatus.num_players, gameStartStatus.player_names);
        this.manageGame();
    }

    startGame() {
        this.smearApiService.gameStart(this.gameId)
                            .subscribe( res => this.checkGameStatus(null),
                                        err => this.handleStartError(err, "Unable to start game, try creating one or joining another game"));
    }

    handleStartError(err: any, message: string) {
        this.welcomeMessage = "";
        this.errorMessage = message + ". " + <any>err;
        console.log(err);
        this.disableCreateButton = false;
        this.disableJoinButton = false;
        this.disableAuthButton = false;
        this.gameIsActive = false;
    }


    //Also reset all globals
    setGameInfo(gameId: string, username: string, teamId: number, numTeams: number, pointsToPlayTo: number, graphPrefix: string):void {
        this.gameId.game_id = gameId;
        this.handService.setGameInfo(gameId, username, teamId, numTeams, pointsToPlayTo, graphPrefix);
        this.numTeams = numTeams;
        for (var i = 0; i < this.numTeams; i++) {
            this.teamMembers.push(new Array<string>());
        }
    }

    saveGameInfoInCookie() {
        Cookie.set('game_id', this.gameAndUser.game_id, 1 /*days from now*/);
        Cookie.set('username', this.gameAndUser.username, 1 /*days from now*/);
    }

    setPlayers(numPlayers: number, playerList: string[]):void {
        this.numPlayers = numPlayers;
        this.players = new Array<Player>();
        for (var i = 0; i < this.numPlayers; i++) {
            this.players.push(new Player(playerList[i], 0, new Array<string>(), this.username == playerList[i]));
        }
        this.handService.setPlayers(this.players);
    }

    getPlayers(): Player[] {
        return this.players;
    }

    getGameAndUser(): GameAndUser {
        return this.gameAndUser;
    }

    getGameId(): GameId {
        return this.gameId;
    }

    getNumPlayers(): number {
        return this.numPlayers;
    }
}
