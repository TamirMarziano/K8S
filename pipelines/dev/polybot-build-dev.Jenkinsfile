pipeline {
    agent any

    options {
        timestamps()
    }

    environment {
        ECR_URL = '352708296901.dkr.ecr.eu-central-1.amazonaws.com/tamirmarz-repo'
    }

    stages {
        stage ('Build and push to ECR') {
            steps {
                sh '''
                aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin 352708296901.dkr.ecr.eu-central-1.amazonaws.com
                cd polybot
                docker build -t polybot-dev:$BUILD_NUMBER .
                docker tag polybot-dev:$BUILD_NUMBER $ECR_URL:polybot-dev_$BUILD_NUMBER
                docker push $ECR_URL:polybot-dev_$BUILD_NUMBER
                '''
            }
        }

        stage ('Trigger Release') {
            steps{
                build job: 'ReleasesDev', wait: false, parameters: [
                    string(name:'IMG_URL', value:"$ECR_URL:polybot-dev:$BUILD_NUMBER")
                ]
            }
        }
    }
}
