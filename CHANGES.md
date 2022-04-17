# headwaters change log

headwaters uses [semver](https://semver.org/) for versioning

## Latest version:

**v0.20.0** - Released 2022-04-15

- **Added**

    - API route versioning: [#30](https://github.com/headwaters-ai/headwaters/issues/30) [commit](https://github.com/headwaters-ai/headwaters/commit/e2cc0ad914a06b2ae90c2c9acd5d972b0e63be21). \
    Versions will match the major version of Headwaters. Currently v0. \
    Add '/v0' to all api calls.

- **Changed**

    - The base url of the local Headwaters server was changed to 'http:127.0.0.1:5555/api' during \
    work on  [#30](https://github.com/headwaters-ai/headwaters/issues/30) [commit](https://github.com/headwaters-ai/headwaters/commit/e2cc0ad914a06b2ae90c2c9acd5d972b0e63be21). 
    This matches the url format of the /ui for consistency.

- **Deprecated** 

    - None
    
- **Removed**

    - None
    
- **Fixed**

    - None
    
- **Security**

    - None
    
## Previous versions:

**v0.19.1** - Released 2022-04-08

- **Added**

    - adjust the frequency of a stream during stream flow [#8](https://github.com/headwaters-ai/headwaters/issues/8) [commit](https://github.com/headwaters-ai/headwaters/commit/a14225da06612d77cd0763b46e9a8f22bde59a97);
    - set burst frequency, volume and trigger burst mode [#9](https://github.com/headwaters-ai/headwaters/issues/9) [commit](https://github.com/headwaters-ai/headwaters/commit/2d76403ce9c003fc8a7bac08a1ef124fd02c1717);

- **Changed**

    - jumped version numbering to broadly follow semver;

- **Deprecated** 

    - None
    
- **Removed**

    - None
    
- **Fixed**

    - None
    
- **Security**

    - None

**v0.0.18** - Released 2022-04-03

- Refactoring changes to standardise class names throughout [#27](https://github.com/headwaters-ai/headwaters/issues/27#issue-1190528788) ([commit](https://github.com/headwaters-ai/headwaters/commit/3113a076224f27e311b946de67057ec3bf237414))