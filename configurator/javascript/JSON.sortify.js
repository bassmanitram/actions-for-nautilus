(function(a){typeof module!="undefined"&&module.exports?module.exports=a():typeof define=="function"&&typeof define.amd=="object"?define("json.sortify",a):JSON.sortify=a()})(function(){/*!
*    Copyright 2015-2017 Thomas Rosenau
*
*    Licensed under the Apache License, Version 2.0 (the "License");
*    you may not use this file except in compliance with the License.
*    You may obtain a copy of the License at
*
*        http://www.apache.org/licenses/LICENSE-2.0
*
*    Unless required by applicable law or agreed to in writing, software
*    distributed under the License is distributed on an "AS IS" BASIS,
*    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
*    See the License for the specific language governing permissions and
*    limitations under the License.
*/"use strict";var a=function(b){if(Array.isArray(b))return b.map(a);if(b instanceof Object){var c=[],d=[];return Object.keys(b).forEach(function(a){/^(0|[1-9][0-9]*)$/.test(a)?c.push(+a):d.push(a)}),c.sort(function(c,a){return c-a}).concat(d.sort()).reduce(function(c,d){return c[d]=a(b[d]),c},{})}return b},b=JSON.stringify.bind(JSON);return function sortify(c,d,e){var f=b(c,d,0);if(!f||f[0]!=="{"&&f[0]!=="[")return f;var g=JSON.parse(f);return b(a(g),null,e)}});