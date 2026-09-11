export * from '../app/index.js';
import {makeYeomanClass} from '../app/index.js';
export default process.env.SBM_GENERATOR_QA==='1' ? class {} : await makeYeomanClass({clone:true});
