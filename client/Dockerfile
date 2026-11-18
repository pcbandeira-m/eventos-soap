FROM maven:3.9-eclipse-temurin-25 AS build
WORKDIR /app
COPY pom.xml .
COPY src ./src
RUN mvn -B package -DskipTests dependency:copy-dependencies -DincludeScope=runtime -DoutputDirectory=target/lib

FROM eclipse-temurin:25-jre
WORKDIR /app
COPY --from=build /app/target/client-*.jar app.jar
COPY --from=build /app/target/lib lib
ENTRYPOINT ["java", "-cp", "app.jar:lib/*", "br.com.estudo.Main"]
