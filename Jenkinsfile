pipeline {
  
  agent any
  tools {
      maven "maven3.9"
  }

  stages {
    stage('Clone Repository') {
      steps {
           sh "echo 'cloning the latest application version' "
           git branch: 'master', changelog: false, poll: false, url: 'https://github.com/georgeebeh/getting-started-app.git'
        }
    }  
    stage('Login Into Docker') {
      steps {
          sh 'docker login --username  --password 
       }
    stage('Build Docker Images') {
      steps {
          sh 'docker build -t georgeebeh/getting-started:latest .'
         }
      }
    }
     stage('Push Images Docker to DockerHub') {
      steps {
          sh 'docker push georgeebeh/getting-started:latest'
    }
  }
    /*post {
      always {
        container('docker') {
          sh 'docker logout'
      }
      }
    }*/
}
}
