export class Player {
    name: string;
    score: number;
    isMe: boolean;
    
    constructor(name: string, isMe: boolean) {
        this.name = name;
        this.score = 0;
        this.isMe = isMe;
    }

    addToScore(hand_score: number):void {
        this.score += hand_score;
    }
}
