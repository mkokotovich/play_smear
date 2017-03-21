import { Card } from './model/card';

export class CardHelper {
    public ranks_lowercase = {
        "2":"2",
        "3":"3",
        "4":"4",
        "5":"5",
        "6":"6",
        "7":"7",
        "8":"8",
        "9":"9",
        "10":"10",
        "Jack":"j",
        "Queen":"q",
        "King":"k",
        "Ace":"a"
    }

    public ranks_uppercase = {
        "2":"2",
        "3":"3",
        "4":"4",
        "5":"5",
        "6":"6",
        "7":"7",
        "8":"8",
        "9":"9",
        "10":"10",
        "Jack":"J",
        "Queen":"Q",
        "King":"K",
        "Ace":"A"
    }

    public suits_lowercase = {
        "Spades":"spades",
        "Hearts":"hearts",
        "Clubs":"clubs",
        "Diamonds":"diams"
    }

    public suits_symbols = {
        "Spades":"&spades;",
        "Hearts":"&hearts;",
        "Clubs":"&clubs;",
        "Diamonds":"&diams;"
    }

    public suits_trump_status = {
        "Spades":"spades",
        "Hearts":"hearts",
        "Clubs":"clubs",
        "Diamonds":"diams"
    }

    getCardClass(card: Card):string {
        return "rank-" + this.ranks_lowercase[card.value] + " " + this.suits_lowercase[card.suit];
    }

    getCardRankUpper(card: Card):string {
        return this.ranks_uppercase[card.value];
    }

    getCardSuitSymbol(card: Card):string {
        return this.suits_symbols[card.value];
    }

    getCardClassFromTrump(trump: string):string {
        return this.suits_trump_status[trump];
    }

    getCardSuitSymbolFromTrump(trump: string):string {
        return this.suits_symbols[trump];
    }

    constructor() { }
}
