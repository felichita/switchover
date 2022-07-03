# switchover

Switching is an application for configuring the kubernetes selector search for the nearest kubernetes node to the patroni cluster

# Service is supported helm
#### Instruction for installation, see bellow 

###*Pay attention to the LABEL*

```console

helm install switchover ./helm -n prod \
        --set imageCredentials.password='$REGISTRY_PASSWORD' \
        --set image.repository='nexus.$ENV:5000/ops/switchover' \
        --set image.tag=$TAG \
        --set imageCredentials.registry='nexus.$ENV:5000' \
        --set vault.token='$VAULT_TOKEN' \
        --set vault.url='http://vault.$ENV:8200' \
        --set label=$LABEL
```

