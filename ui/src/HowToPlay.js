import React, { Component } from 'react';
import { withRouter, Link } from 'react-router-dom';

function HowToPlay(props) {
    const rules = (
        <div style={{padding: "20px 20px 20px 20px"}}>
        <Link style={{fontSize: "large"}} to="/">Bring me back to start a game!</Link>
        <br/>
        <h1>How To Play Smear</h1>
        <p>
        There are many different ways to play smear; every region has their own "house rules". This site uses the rules that my family plays by, I'll explain them here.
        </p>
        <h2>Overview</h2>
        <p>
        Smear (also known as Schmier, and a variety of Pitch or Setback) is a trick-taking card game where points are won not by taking tricks, but by taking certain cards during the course of the hand. Everyone is dealt six cards, and then places a bid based on how many points they think they can get. The high bidder gets to pick which suit will be trump, and plays the first card. After all tricks have been played, points are awarded. Once someone reaches 11 (or whatever score is agreed upon at the beginning of the game) then the game is over, and that player wins.
        </p>
        <p>
        There is one alternate rule to ending the game! Some people play where a player can only win the game by winning a bid. If the first player to go over 11 (or whatever score is agreed upon) does so by taking home Low or other points, but not while winning a bid, that player does not win the game until they make a bid. This mode can be enabled by selecting "Require a winning bid to go out" when creating a game.
        </p>
        <h2>Points</h2>
        <p>
        There are a maximum of five points per hand. However, not all points are out during each hand.
        </p>
        <p>
        <b>High</b> - A point is awarded for the highest card of trump.
        </p>
        <p>
        <b>Low</b> - A point is awarded for the lowest card of trump. The player who is dealt the lowest card of trump automatically wins the point; there is no requirement to take the card home.
        </p>
        <p>
        <b>Jack</b> - A point is awarded for the jack of trump. The player who wins the jack of trump in a trick receives the point. 
        </p>
        <p>
        <b>Jick</b> - A point is awarded for the jack of the same color as trump. For example, if trump is Hearts, the Jack of Diamonds is the Jick of trump. The Jick is regarded as trump, not the suit that is shown on the card. The player who wins Jick in a trick receives the point. 
        </p>
        <p>
        <b>Game</b> - Certain cards are assigned Game Points:
        </p>
        <table>
            <tr>
                <td>
                    10
                </td>
                <td>
                    10 game points
                </td>
            </tr>
            <tr>
                <td>
                    Ace
                </td>
                <td>
                    4 game points
                </td>
            </tr>
            <tr>
                <td>
                    King
                </td>
                <td>
                    3 game points
                </td>
            </tr>
            <tr>
                <td>
                    Queen
                </td>
                <td>
                    2 game points
                </td>
            </tr>
            <tr>
                <td>
                    Jack
                </td>
                <td>
                    1 game points
                </td>
            </tr>
        </table>
        <p>
        At the end of the hand, each player adds up the Game Points from the tricks they have won. The player with the most Game Points is awarded Game.
        </p>
        <h2>Bidding</h2>
        <p>
        The player after the dealer (in a clock-wise rotation) is the first to bid. Each player will bid how many points they think they will win in the hand. The high bidder gets to pick trump, and lead the first card. Each player only bids once - "raising" a bid is not allowed.
        </p>
        <h2>Playing a trick</h2>
        <h3>Leading</h3>
        <p>
        The bidder leads the first trick. Then, the winner of each trick leads the next trick.
        </p>
        <h3>Following suit</h3>
        <p>
        Players are required to follow suit. For example, if the lead card is trump, everyone else needs to play trump. There are two cases where players are not required to follow suit: when a player doesn't have any cards of that suit, or if a player wishes to play trump instead. A player is allowed to trump in at any time.
        </p>
        <h3>Taking a trick</h3>
        <p>
        If trump is lead, then the highest trump played takes the trick. If a non-trump suit is lead, than the highest card of that suit played takes the trick, unless there were any trump played, in which case the highest trump played takes the trick. The order of trump goes: Ace, King, Queen, Jack, Jick, 10, 9, 8, 7, 6, 5, 4, 3, and 2.
        </p>
        <h3>Scoring</h3>
        <p>
        If the bidder won as least as many points as was bid, those points are added to the bidder's score. If the bidder won less points then was bid, the bidder is "set", and the bid is subtracted from the bidder's score. Any other players who won points during the hand have those points added to their scores.
        </p>
        <h2>Winning</h2>
        <p>
        At start of the game, players choose a number of points to play to, typically 11, 15, or 21. Once the first player's score matches or exceeds that total, the game is over and that player wins. If the bidder and one or more other players all go over on the same hand, the bidder always wins, regardless of who has more points.
        </p>
        </div>
    );

    return rules;
}

export default withRouter(HowToPlay);
