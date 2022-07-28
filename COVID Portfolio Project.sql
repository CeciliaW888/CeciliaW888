SELECT *
FROM CovidDeath
WHERE continent is not null
ORDER BY 3,4

--SELECT *
--FROM CovidVaccination
--ORDER BY 3,4

SELECT location, date, total_cases, new_cases, total_deaths, population
FROM CovidDeath
WHERE continent is not null
ORDER BY 1,2

--Looking at Total Cases vs Total Deaths in Australia
SELECT location, date, total_cases, total_deaths, (total_deaths/total_cases)*100 AS DeathPercentage
FROM CovidDeath
WHERE location like 'Australia'
ORDER BY 1,2

--Looking at Total Cases vs Population in Australia
SELECT location, date, total_cases, population, (total_cases/population)*100 AS InfectionPercentage
FROM CovidDeath
WHERE location like 'Australia'
ORDER BY 1,2

--Looking at countries with the highest infection rate compared to population
SELECT location, population, MAX(total_cases) AS HighestInfectionCount,  MAX(total_cases/population)*100 AS InfectionPercentage
FROM CovidDeath
WHERE continent is not null
GROUP BY location, population
ORDER BY InfectionPercentage DESC

--Looking at the highest death count per population
SELECT location, MAX(cast(total_deaths AS INT)) AS TotalDeathCount 
FROM CovidDeath
WHERE continent is not null
GROUP BY location
ORDER BY TotalDeathCount DESC

--Let's break things down by continent
SELECT location, MAX(cast(total_deaths AS INT)) AS TotalDeathCount 
FROM CovidDeath
WHERE continent is null AND location not like '%income%'
GROUP BY location
ORDER BY TotalDeathCount DESC

--Showing the continents with the highest deathcount
SELECT continent, MAX(cast(total_deaths AS INT)) AS TotalDeathCount 
FROM CovidDeath
WHERE continent is not null
GROUP BY continent
ORDER BY TotalDeathCount DESC

--Global numbers by date
SELECT date, SUM(new_cases)AS total_cases, SUM(CAST(new_deaths AS INT)) AS total_deaths, SUM(CAST(new_deaths AS INT))/SUM(new_cases)*100 AS DeathPercentage
FROM CovidDeath
WHERE continent is not null
GROUP BY date
ORDER BY 1,2

--Global numbers in total
SELECT SUM(new_cases)AS total_cases, SUM(CAST(new_deaths AS INT)) AS total_deaths, SUM(CAST(new_deaths AS INT))/SUM(new_cases)*100 AS DeathPercentage
FROM CovidDeath
WHERE continent is not null
ORDER BY 1,2

--Looking at Total Population vs Vaccination
SELECT d.continent, d.location, d.date, d.population, v.new_vaccinations, 
SUM(CONVERT(INT, v.new_vaccinations)) OVER(PARTITION BY d.location ORDER BY d.location, d.date) AS rolling_num_vac
FROM CovidDeath d
JOIN CovidVaccination v
	ON d.location = v.location
	AND d.date = v.date
WHERE d.continent IS NOT null
ORDER BY 2,3

--Use CTE
With PopvsVac(continent, location, date, population, new_vaccination, rolling_num_vac)
AS 
(SELECT d.continent, d.location, d.date, d.population, v.new_vaccinations, 
SUM(CONVERT(INT, v.new_vaccinations)) OVER(PARTITION BY d.location ORDER BY d.location, d.date) AS rolling_num_vac
FROM CovidDeath d
JOIN CovidVaccination v
	ON d.location = v.location
	AND d.date = v.date
WHERE d.continent IS NOT null
)
SELECT *, (rolling_num_vac/population)*100 AS vac_rate
FROM PopvsVac
 
--Use Temp table
DROP TABLE IF EXISTS #PercentPopulationVaccinated
CREATE TABLE #PercentPopulationVaccinated
(
continent nvarchar(255),
location nvarchar(255),
date datetime,
population int,
new_vaccinations int,
rolling_num_vac int,
)
INSERT INTO #PercentPopulationVaccinated
SELECT d.continent, d.location, d.date, d.population, v.new_vaccinations, 
SUM(CONVERT(INT, v.new_vaccinations)) OVER(PARTITION BY d.location ORDER BY d.location, d.date) AS rolling_num_vac
FROM CovidDeath d
JOIN CovidVaccination v
	ON d.location = v.location
	AND d.date = v.date
WHERE d.continent IS NOT null

SELECT *, (rolling_num_vac/population)*100 AS vac_rate
FROM #PercentPopulationVaccinated

--Create a view
CREATE VIEW PercentPopulationVaccinated AS
SELECT d.continent, d.location, d.date, d.population, v.new_vaccinations, 
SUM(CONVERT(INT, v.new_vaccinations)) OVER(PARTITION BY d.location ORDER BY d.location, d.date) AS rolling_num_vac
FROM CovidDeath d
JOIN CovidVaccination v
	ON d.location = v.location
	AND d.date = v.date
WHERE d.continent IS NOT null

 