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
                cd yolo5
                docker build -t yolo5-dev:$BUILD_NUMBER .
                docker tag yolo5-dev:$BUILD_NUMBER $ECR_URL:yolo5-dev_$BUILD_NUMBER
                docker push $ECR_URL:yolo5-dev_$BUILD_NUMBER
                '''
            }
        }

        stage ('Trigger Release') {
            steps{
                build job: 'ReleasesDev', wait: false, parameters: [
                    string(name:'IMG_URL', value:"$ECR_URL:yolo5-dev:$BUILD_NUMBER")
                ]
            }
        }
    }
}
