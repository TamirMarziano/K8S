pipeline{
    agent any

    parameters { string(name: 'IMG_URL', defaultValue: '', description: '') }

    stages{
        stage ('Update YAML'){
            steps {
                withCredentials([usernamePassword(credentialsId: 'GitHub', usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD')]) {
                   sh '''
                   echo $IMG_URL
                   if [[ ${IMG_URL} =~ "polybot" ]]; then
                        YAML="k8s/prod/polybot_deployment.yaml"
                   else
                        YAML="k8s/prod/yolo5_deployment.yaml"
                   fi

                   git config --global user.email "marzianotamir@gmail.com"
                   git config --global user.name "TamirMarziano"

                   git checkout release
                   git pull
                   git merge origin/master
                   sed -i "s|image: .*|image: ${IMG_URL}|g" $YAML
                   git add $YAML
                   git commit -m "Updating IMG_URL"
                   git push https://TamirMarziano:$PASSWORD@github.com/TamirMarziano/K8S.git release
                   '''
                }
            }

        }
    }

}