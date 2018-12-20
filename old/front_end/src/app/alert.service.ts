import { Injectable } from '@angular/core';

@Injectable()
export class AlertService {

    private alerts: any = [];

    constructor() { }

    addAlert(typeStr: string, msgStr: string, dismissibleVal:boolean = true) {
        this.alerts.push({
            type: typeStr,
            msg: msgStr,
            dismissible: dismissibleVal
        });
    }

    clearAlerts(forceAll = false) {
        if (forceAll) {
            this.alerts.length = 0;
        } else {
            for (var i = this.alerts.length - 1; i >= 0; i--) {
                if (this.alerts[i].dismissible) { 
                    this.alerts.splice(i, 1);
                }
            }
        }
    }

    getAlerts(): any[] {
        return this.alerts;
    }
}
