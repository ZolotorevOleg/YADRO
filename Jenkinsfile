pipeline {
    agent {
        label 'currency'
    }

    options {
        gitLabConnection('education-git.yadro.com')
    }

    environment {
        HADOLINT_IMAGE = 'hadolint/hadolint:v2.14.0-alpine@sha256:7aba693c1442eb31c0b015c129697cb3b6cb7da589d85c7562f9deb435a6657c'
    }

    stages {
        stage('requirements') {
            steps {
                gitlabCommitStatus('requirements') {
                    sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install -r requirements.txt
                    '''
                }
            }
        }

        stage('lint') {
            steps {
                gitlabCommitStatus('lint') {
                    sh '''
                    . venv/bin/activate
                    flake8 main.py test_app.py services utils infrastructure
                    docker run -i --rm $HADOLINT_IMAGE < Dockerfile
                    '''
                }
            }
        }

        stage('test') {
            steps {
                gitlabCommitStatus('test') {
                    sh '''
                    . venv/bin/activate
                    pytest --junit-xml=tests.xml test_app.py
                    '''
                }
                junit 'tests.xml'
            }
        }

        stage('build') {
            steps {
                gitlabCommitStatus('build') {
                    script {
                        if (env.GIT_BRANCH == 'origin/main') {
                            input message: 'Запустить сборку для main?'
                        }
                    }
                sh 'docker-compose build'
                }
            }
        }

        stage('deploy') {
            when {
                expression {
                    env.GIT_BRANCH == 'origin/main'
                }
            }
            steps {
                gitlabCommitStatus('deploy') {
                    script {
                        if (env.GIT_BRANCH == 'origin/main') {
                            input message: 'Запустить деплой для main?'
                            sh 'docker-compose up -d'
                        }
                    }
                }
            }
        }
    }
}