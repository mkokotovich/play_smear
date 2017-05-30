import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { GraphLoaderComponent } from './graph-loader.component';

describe('GraphLoaderComponent', () => {
  let component: GraphLoaderComponent;
  let fixture: ComponentFixture<GraphLoaderComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ GraphLoaderComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(GraphLoaderComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
