import {Component, OnInit, Input} from '@angular/core';

import {NgbModal, NgbActiveModal} from '@ng-bootstrap/ng-bootstrap';

@Component({
  selector: 'app-hand-status-modal',
  templateUrl: './hand-status-modal.component.html',
  styleUrls: ['./hand-status-modal.component.css']
})

export class HandStatusModalComponent implements OnInit {
    @Input() handStatus;

    constructor(public activeModal: NgbActiveModal) { }

    ngOnInit() {
    }

}
