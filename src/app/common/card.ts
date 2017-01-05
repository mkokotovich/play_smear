export class Card {
    suit: string;
    value: string;
    
    constructor(suit: string, value: string) {
        this.suit = suit;
        this.value = value;
    }

    abbrev(): string {
        return this.suit + this.value;
    }
}
