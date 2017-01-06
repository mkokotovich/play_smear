/* tslint:disable:no-unused-variable */

import { TestBed, async, inject } from '@angular/core/testing';
import { HandService } from './hand.service';

describe('HandService', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [HandService]
    });
  });

  it('should ...', inject([HandService], (service: HandService) => {
    expect(service).toBeTruthy();
  }));
});
