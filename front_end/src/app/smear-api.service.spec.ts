/* tslint:disable:no-unused-variable */

import { TestBed, async, inject } from '@angular/core/testing';
import { SmearApiService } from './smear-api.service';

describe('SmearApiService', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [SmearApiService]
    });
  });

  it('should ...', inject([SmearApiService], (service: SmearApiService) => {
    expect(service).toBeTruthy();
  }));
});
