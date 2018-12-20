export class Player {
    constructor(
        public name: string,
        public score: number,
        public points: Array<string>,
        public isMe: boolean) {
    }

    addToScore(hand_score: number):void {
        this.score += hand_score;
    }
}
