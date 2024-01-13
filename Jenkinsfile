pipeline {
    agent any

    environment {
        PROD_USERNAME = 'amedikusettor'
        PROD_SERVER = '34.121.116.117'
        PROD_DIR = '/home/amedikusettor/myflix/movie-upload'
        DOCKER_IMAGE_NAME = 'movie-upload-deployment'
        DOCKER_CONTAINER_NAME = 'movie-upload'
        DOCKER_CONTAINER_PORT = '6001'
        DOCKER_HOST_PORT = '6001'
    }

    stages {
        stage('Load Code to Workspace') {
            steps {
                // This step automatically checks out the code into the workspace.
                checkout scm             
            }
        }

        stage('Deploy Repo to DB Server') {
            steps {
                script {
                    sh 'echo Packaging files ...'
                    sh 'tar -czf movieupload_files.tar.gz *'
                    sh "scp -o StrictHostKeyChecking=no movieupload_files.tar.gz ${PROD_USERNAME}@${PROD_SERVER}:${PROD_DIR}"
                    sh 'echo Files transferred to server. Unpacking ...'
                    sh "ssh -o StrictHostKeyChecking=no ${PROD_USERNAME}@${PROD_SERVER} 'pwd && cd myflix/movie-upload && tar -xzf movieupload_files.tar.gz && ls -l'"
                    sh 'echo Repo unloaded on Prod. Server. Preparing to dockerize application ..'
                }
            }
        }

        stage('Dockerize GCP Upload Interface') {
            steps {
                script {
                    sh "ssh -o StrictHostKeyChecking=no ${PROD_USERNAME}@${PROD_SERVER} 'cd myflix/movie-upload && docker build -t ${DOCKER_IMAGE_NAME} .'"
                    sh "echo Docker image for movieUpload rebuilt. Preparing to redeploy container to web..."
                }
            }
        }

        stage('Redeploy Container to Web') {
            steps {
                script {
                    sh "ssh -o StrictHostKeyChecking=no ${PROD_USERNAME}@${PROD_SERVER} 'cd myflix/movie-upload && docker ps -q --filter name=${DOCKER_CONTAINER_NAME} | xargs -r docker stop'"
                    sh "ssh -o StrictHostKeyChecking=no ${PROD_USERNAME}@${PROD_SERVER} 'cd myflix/movie-upload && docker ps -q --filter name=${DOCKER_CONTAINER_NAME} | xargs -r docker rm'"

                    sh "echo Container stopped and removed. Preparing to redeploy new version"
                    sh "ssh -o StrictHostKeyChecking=no ${PROD_USERNAME}@${PROD_SERVER} 'cd myflix/movie-upload && docker run -d -p ${DOCKER_HOST_PORT}:${DOCKER_CONTAINER_PORT} --name ${DOCKER_CONTAINER_NAME} ${DOCKER_IMAGE_NAME}'"
                    sh "echo movieUpload Microservice Deployed!"
                }
            }
        }
    }
}
