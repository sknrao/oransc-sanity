Current Status:

Total Pods: 303
Running Pods: 226

=== **Non-Running Pods** (ONAP) ===
NAME                                                        READY   STATUS                  RESTARTS         AGE
cassandra-dc1-default-sts-0                                 0/3     Pending                 0                66m
cassandra-dc1-default-sts-1                                 0/3     Pending                 0                54m
onap-aai-6f7ff868b8-gszpn                                   1/2     CrashLoopBackOff        27 (2m31s ago)   78m
onap-aai-graphadmin-697bb59c75-mcmw6                        1/2     Init:2/5                7 (5m28s ago)    78m
onap-aai-resources-5b48cb98c9-592k4                         1/2     Init:2/3                0                78m
onap-aai-sparky-be-b5854549-6mvhw                           1/2     Init:2/3                7 (5m31s ago)    78m
onap-aai-traversal-5df75f56b8-4wdgs                         1/2     Init:2/3                0                78m
onap-authentication-oauth2-proxy-7c5bd88bc6-8cf44           1/2     CrashLoopBackOff        29 (16s ago)     78m
onap-authentication-onap-keycloak-config-cli-8w294          0/2     Error                   0                78m
onap-authentication-onap-keycloak-config-cli-bc5r8          0/2     Error                   0                75m
onap-authentication-redis-server-1                          0/4     Pending                 0                2m34s
onap-cds-sdc-listener-65d5746d85-26fhs                      1/2     Init:2/3                2 (16m ago)      78m
onap-cps-postgres-init-config-job-z2hjz                     0/2     Completed               0                44m
onap-dcae-ves-openapi-manager-7998f7cc66-8vlx2              1/2     Init:2/3                2 (16m ago)      78m
onap-nengdb-init-config-job-cmkmk                           0/2     Completed               0                74m
onap-portal-ng-history-postgres-init-config-job-bz27k       0/2     Completed               0                74m
onap-portal-ng-preferences-postgres-init-config-job-z52gs   0/2     Completed               0                74m
onap-portal-ng-ui-57c77dfc8c-m6lc7                          1/2     CrashLoopBackOff        6 (2m11s ago)    8m4s
onap-portal-ng-ui-6c7896d7-ct66q                            1/2     CrashLoopBackOff        14 (2m16s ago)   74m
onap-sdc-be-4qf8j                                           0/2     Init:Error              0                74m
onap-sdc-be-76b479c868-qm9b8                                1/2     Init:2/4                5 (31s ago)      74m
onap-sdc-be-qvgt7                                           0/2     Init:Error              0                26m
onap-sdc-be-tt8qj                                           0/2     Pending                 0                43s
onap-sdc-cs-4dfg8                                           1/2     Init:2/3                0                9m42s
onap-sdc-cs-cxftq                                           0/2     Init:Error              0                74m
onap-sdc-cs-jq2c8                                           0/2     Init:Error              0                30m
onap-sdc-cs-wlbkh                                           0/2     Init:Error              0                20m
onap-sdc-cs-zf6wq                                           0/2     Init:Error              0                41m
onap-sdc-fe-6c4c9ff88c-mzkdw                                1/2     Init:2/4                5 (40s ago)      74m
onap-sdc-onboarding-be-64c9fbb795-whxq6                     1/2     Init:2/4                2 (98s ago)      74m
onap-sdc-onboarding-be-l7kj5                                0/2     Init:Error              0                31m
onap-sdc-onboarding-be-qkr7t                                0/2     Init:Error              0                74m
onap-sdc-onboarding-be-w9b7f                                1/2     Init:2/3                0                11m
onap-sdc-wfd-be-689b545d7d-xn6q7                            1/2     Init:2/3                2 (10m ago)      74m
onap-sdc-wfd-be-b2bbf                                       1/2     Init:2/3                0                10m
onap-sdc-wfd-be-fdcpr                                       0/2     Init:Error              0                31m
onap-sdc-wfd-be-m8tgt                                       0/2     Init:Error              0                41m
onap-sdc-wfd-be-xxz4c                                       0/2     Init:Error              0                20m
onap-sdc-wfd-be-xzpqg                                       0/2     Init:Error              0                74m
onap-sdc-wfd-fe-b99d5cf86-drjzt                             1/2     Init:2/3                6 (41s ago)      74m
onap-sdnc-0                                                 1/2     Init:3/5                0                74m
onap-sdnc-ansible-server-bb4ddd684-9rf8q                    1/2     Init:3/4                4 (10m ago)      74m
onap-sdnc-dbinit-job-brtfk                                  0/2     Completed               0                74m
onap-sdnc-sdnrdb-init-job-5hdlb                             0/2     Init:Error              0                30m
onap-sdnc-sdnrdb-init-job-6xqwx                             0/2     Init:Error              0                40m
onap-sdnc-sdnrdb-init-job-cpnjn                             0/2     Init:Error              0                74m
onap-sdnc-sdnrdb-init-job-gw6l6                             0/2     Init:Error              0                19m
onap-sdnc-sdnrdb-init-job-qz84w                             0/2     Pending                 0                9m10s
onap-sdnc-ueb-listener-b9fc948f6-9h8gf                      1/2     Init:3/4                0                74m
onap-sdnc-web-5767cb98bc-284zz                              1/2     Init:2/3                5 (11s ago)      74m
onap-sdnrdb-coordinating-only-6757cd6478-9nh2x              1/3     Init:ImagePullBackOff   0                74m
onap-sdnrdb-master-0                                        1/2     Init:ImagePullBackOff   0                74m
onap-so-mariadb-config-job-wln7v                            0/2     Completed               0                37m
onap-so-sdc-controller-59b9b89c4d-xznv5                     1/2     Init:2/3                1 (21m ago)      71m
onap-uui-intent-analysis-init-postgres-dwzhz                0/2     Completed               0                45m
onap-uui-llm-adaptation-init-postgres-2982n                 0/2     Completed               0                45m
onap-uui-server-shhxp                                       0/2     Completed               0                45m

=== Portal & OAuth2 Context ===
onap-authentication-oauth2-proxy-7c5bd88bc6-8cf44           1/2     CrashLoopBackOff        29 (16s ago)     78m
onap-portal-ng-ui-57c77dfc8c-m6lc7                          1/2     CrashLoopBackOff        6 (2m11s ago)    8m4s
onap-portal-ng-ui-6c7896d7-ct66q                            1/2     CrashLoopBackOff        14 (2m16s ago)   74m
agnik@agnik-Alpha-15-A3DD:~/Desktop/deployoran$
