# Setting Up Development Tools To Use the UPS Proxy

Developing on UPS workstations requires setting up connection through the UPS proxy for most development tools. Tools such as `git` can read proxy authentication settings from system environment variables.

## Instructions

1. In command prompt, run the following command exactly as is:

    ```bat
    rundll32 sysdm.cpl,EditEnvironmentVariables
    ```

1. From the launched window, click `New...` button to add an environment variable.

    ![Windows Environment Variables Prompt](pics/windows-env-vars.png)

1. In this window, add an environment variable called `HTTP_PROXY`. It's value should be `http://adid:password@proxy.ups.com:8080/`

    > ⚠️ Replace `adid` and `password` with your credentials, keeping the `:` colon. Special characters in your password will have to be encoded correctly within the proxy URL. For example, `PASS@WORD` will have to be entered as `PASS%40WORD`

    Please use this reference for replacing special characters in your password:

    |  !  |  #  |  $  |  &  |  '  |  (  |  )  |  *  |  +  |
    |:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
    | %21 | %23 | %24 | %26 | %27 | %28 | %29 | %2A | %2B |

    |  ,  |  /  |  :  |  ;  |  =  |  ?  |  @  |  [  |  ]  |
    |:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
    | %2C | %2F | %3A | %3B | %3D | %3F | %40 | %5B | %5D |

    ![HTTP_PROXY](pics/http-proxy.png)

1. Add another environment variable called `HTTPS_PROXY`, using the same value as `HTTP_PROXY` (including `http://`).

    ![HTTPS_PROXY](pics/https-proxy.png)

1. Add another environment variable called `NO_PROXY`. This will contain a list of hosts to not use the proxy for:

    ```plaintext
    .ups.com,.ams1907.com,localhost,127.0.0.1
    ```

    ![NO_PROXY](pics/no-proxy.png)

1. next run the following commands:

    ```sh
    git config --global --unset http.proxy
    git config --global --unset https.proxy
    git config --global http.proxyAuthMethod 'basic'
    git config --global http.sslVerify false
    ```

1. close your current command prompt and open a new command prompt. To clone the repository, in a folder of your choice run:

    ```
    git clone `<your team's github repo url>`
    ```

    A sample can be seen below:

    ```
    git clone https://github.com/UPS-2023-Hackathon/team-0-sample.git 
    ```