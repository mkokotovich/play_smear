import { SmearPage } from './app.po';

describe('smear App', function() {
  let page: SmearPage;

  beforeEach(() => {
    page = new SmearPage();
  });

  it('should display message saying app works', () => {
    page.navigateTo();
    expect(page.getParagraphText()).toEqual('app works!');
  });
});
