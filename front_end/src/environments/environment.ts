// The file contents for the current environment will overwrite these during build.
// The build system defaults to the dev environment which uses `environment.ts`, but if you do
// `ng build --env=prod` then `environment.prod.ts` will be used instead.
// The list of which env maps to which file can be found in `angular-cli.json`.

import { constants } from '../host-specific-constants';

export const environment = {
  production: false,
  //apiBaseUrl: constants.apiServerAddress
  apiBaseUrl: "http://192.168.86.200:5000"
};
