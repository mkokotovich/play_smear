export class Card {
    suit: string;
    value: string;
    selected: boolean;
    
    constructor(suit: string, value: string) {
        this.suit = suit;
        this.value = value;
        this.selected = false;
    }

    abbrev(): string {
        return this.suit + this.value;
    }
}
