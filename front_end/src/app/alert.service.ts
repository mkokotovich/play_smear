import { Injectable } from '@angular/core';

@Injectable()
export class AlertService {

    private alerts: any = [];

    constructor() { }

    addAlert(typeStr: string, msgStr: string) {
        this.alerts.push({
            type: typeStr,
            msg: msgStr
        });
    }

    clearAlerts() {
        this.alerts.length = 0;
    }

    getAlerts(): any[] {
        return this.alerts;
    }
}
