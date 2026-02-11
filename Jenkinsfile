pipeline {
    agent {
        label "zuvmljenson02"
    }
    environment {
        IMAGE_PYTHON = 'registry.lksnext.com/devsecops/python3_12:1.0'
        IMAGE_SONARSCANNER = 'registry.lksnext.com/devsecops/custom-sonarscanner-cli:1.0'
        SONAR_ENTERPRISE_HOST_URL = 'https://sonarqubeenterprise.devops.lksnext.com/'
        SONAR_TOKEN = credentials('sonarenterprise-analysis-token')
        PROJECT_NAME = 'lks-idprovider'
        NEXUS_CREDENTIALS = credentials('registryCredential') 
    }
    stages {
        stage('Test Coverage') {
            when {
                environment name: 'JOB_ACTION', value: 'sonar'
            }
            steps {
                script {
                    sh '''
                        docker run --rm \
                        -v ./:/app \
                        -w /app \
                        -e NEXUS_USER=$NEXUS_CREDENTIALS_USR \
                        -e NEXUS_PASSWORD=$NEXUS_CREDENTIALS_PSW \
                        $IMAGE_PYTHON \
                        sh -c '
                            # Configura poetry para autenticarse en los repositorios de Nexus
                            poetry config http-basic.lks-next-all "$NEXUS_USER" "$NEXUS_PASSWORD" &&
                            poetry config http-basic.lksnexus-pypi "$NEXUS_USER" "$NEXUS_PASSWORD" &&

                            find . -name pyproject.toml -exec dirname {} \\; | while read -r dir; do
                                echo "--- Running tests in $dir ---"
                                (
                                    cd "$dir" && \
                                    # Instala dependencias, incluyendo las de desarrollo (dev)
                                    poetry install --with dev && \
                                    # Print directory content
                                    echo "Directory $dir content:"
                                    ls -la && \
                                    # Run tests with coverage
                                    poetry run pytest --cov=. --cov-report=xml --ignore=**/integration
                                )
                                # Create a clean name from the directory path
                                report_name=$(echo "$dir" | sed "s|\\./||" | sed "s|/|-|g")
                                # Move and rename coverage file to the root
                                mv "$dir/coverage.xml" "./coverage-$report_name.xml"
                            done
                        '
                    '''
                }
            }
        }
        stage('Sonar') {
            when {
                environment name: 'JOB_ACTION', value: 'sonar'
            }
            steps {
                script {
                    sh '''
                        docker run --rm \
                        -v ./:/app \
                        -e SONAR_HOST_URL=$SONAR_ENTERPRISE_HOST_URL \
                        -e SONAR_TOKEN=$SONAR_TOKEN \
                        $IMAGE_SONARSCANNER \
                        -Dsonar.projectKey=$PROJECT_NAME \
                        -Dsonar.projectBaseDir=/app \
                        -Dsonar.sources=/app \
                        -Dsonar.branch.name=develop \
                        -Dsonar.python.version=3.10 \
                        -Dsonar.python.coverage.reportPaths=coverage-*.xml \
                        -Dsonar.exclusions=coverage-*.xml
                    '''
                }
            }
        }
    }
    post {
        always {
            deleteDir()
        }
    }
}