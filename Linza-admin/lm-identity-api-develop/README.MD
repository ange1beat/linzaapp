# Identity API

Install dependencies:
At the command prompt, run the dotnet restore command. This command loads all dependencies specified in the *.csproj file, including NuGet packages.

dotnet reactor

Build the project:
After restoring the dependencies, run the dotnet build command to build the project.

dotnet build

Upload the project using .NET CLI:
Use the donut run command

donut run

To stock a project, a web application ASP.NET will be available on request http://localhost:5000 . If you use HTTPS, then everything will be fine https://localhost:5001 .

If you want to know how to do this, use the <url> --urls option:

dotnet run --url=http://localhost:8080

For local testing, a postgresql database of the latest version is needed, the entire project together with the database can be raised via docker-compose command:
docker-compose up

**TBD**