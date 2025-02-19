# Stack Overflow 2022-2024 Survey Analysis

The Stack Overflow developer surveys contain questions regarding demographics info, education and professional experiences, developer types and compensations and organizational questions like employee counts, whether respondents work remotely or in person and how much time they spend providing guidance to or seeking guidance from their coworkers. As these surveys change over the years, either in how each question is formatted or in the asked questions, they need to be comprehensively analyzed and cleaned in order for healthy comparisons to be made between the years. 
This analysis is mostly focused on how compensation of respondents changed in time, based on different factors like age, country, seniority, education level and job responsibilities, but supporting data is also included

[Tableau Visualization Link](https://public.tableau.com/views/StackOverflowSurveyAnalysis2022-2024/Overview?:language=en-US&:sid=&:redirect=auth&:display_count=n&:origin=viz_share_link)

## Takeaways

Looking at the data available, we can derive the following insights:

  - NoSQL database usage is in the rise, as both the supply and the demand for unstructured data rises
  - Compensation is linearly dependent on seniority and education level for the most part, but entry-level positions' pay has gone down
  - Online learning methods' popularity is increasing with each year, though bias must be accounted for as this survey is aimed at an online community
  - Demand for Python is disproportionately higher than its actual usage, even considering its rise in professional work, especially among data-related work like business analysts and data scientists
  - The data in this anonymized, public-access survey is not entirely reliable (the most egregious example being that 37 respondents identified as younger than 24 with more than 18 years of coding experience), so common sense and intuition is invaluable when parsing it

The steps taken to arrive at these results are listed below.


## Data Cleaning and Merging Work (Python)

The Python code to clean the data is written such that making adjustments to include or exclude years in this analysis is straightforward. However, as the gap in years grows it becomes more taxing to parse the data manually, and the count of rows makes running SQL operations on the dataframes much more slow, so this project is limited to the years 2022, 2023 and 2024. The dataframe for year 2022 has 73268 rows and 80 columns, the dataframe for 2023 has 89184 rows and 85 columns, and finally for 2024 we have 65437 rows and 115 columns, where the response IDs are no longer unique since they track responses per year, so we redefine a response ID column based on row index.

Once we drop columns that correspond to questions that aren't consistent among years and merge all 3 dataframes, we are left with 227889 rows and 63 columns, at which point we face two major issues:
  - The data is highly unorganized and chaotic
  - Certain rows correspond to checklist questions, where respondents can tick multiple answers, which is then stored as semicolon-separated strings
In order to make the dataframes easier to work with, we utilize the following solutions to these problems:
  - Bucket the columns based on their relations to one another, and split the dataframes based on these relations rather than years
  - Separate these semicolon-separated columns into multiple boolean columns

The buckets we separate the columns into are as follows:
  - **HaveWorkedWith**, which stores the dataframes that contain the boolean columns that track whether a correspondent uses a certain tech or not (eg. databases, coding languages, platforms etc.)
  - **WantToWorkWith**, which stores the dataframes that contain the boolean columns that track whether a correspondent wants to use a certain tech or not
  - **BooleanDataframes**, which stores the dataframes that contain other boolean columns that don't fit in either category, but are too large on their own to be combined, so they're kept as their own separate dataframes. These are:
    - **BuyNewTool**, which tracks how respondents make the decision to buy new tools, such as starting a free trial or asking other professionals
    - **CodingActivities**, which tracks coding activities respondents engage with outside of their work, like contributing to open-source projects
    - **DevType**, which tracks how the respondents self-identify their work titles, such as Data Scientist, Full-stack Developer or Database Admin
    - **Employment**, which tracks employment status, like unemployed but looking for work, retired or in full-time employment
    - **LearnCode**, which tracks how respondents learned to code, such as books, school or on-the-job training
    - **LearnCodeOnline**, which tracks online learning methods respondents use, like tutorial videos, blogs or forums
    - **NEWSOSites**, which tracks the respondents' engagement with websites on the Stack Overflow network
    - **OpSysPersonal_use** and **OpSysProfessional_use**, which tracks which operation systems respondents use in daily life and at work, respectively
    - **ProfessionalTech**, which tracks which technologies respondents have access to at work, like automated testing

Then we have the dataframes that correspond to existing columns of the dataframe, which weren't split into boolean columns:
  - **BasicInfo**, which tracks the survey response year, age and country
  - **EduWork**, which stores education and career related info, like the highest education degree the respondent has, years of coding experience and yearly compensation
  - **ProfDevSeries**, which stores the questions in the survey under the Professional Developer Series umbrella not already covered by one of the boolean column dataframes, like how much time respondents spend answering or asking questions at work
  - **SOInfo**, which stores respondents' Stack Overflow related habits that don't fall under the NEWSOSites dataframe's umbrella
  - **Misc**, which stores everything not manually inserted into one of the other categories

As the dataframes that store info as multiple boolean columns have edge cases where the majority of rows have one or two positive entries with dozens of blank values, these dataframes are also stored in an alternate pivoted format, where, rather than storing everything in a multitude of columns with unique respondent IDs, the data is stored in two columns; one to store the responses as strings and another to store respondent IDs (which is no longer necessarily unique within the dataframe itself as respondents can have multiple answers to these questions). This format is not necessarily more efficient depending on the initial dataframe, but is easier to work with when using certain BI programs like Tableau than it would be otherwise, so rather than storing these dataframes as just these pivoted versions, they're stored in separate subfolders in this format to use when it makes more sense than to use the initial version.

## Visualization Work (SQL and Tableau)

By joining the previously separated dataframes by their response ID columns, we can work with only the data we want to work with, which greatly improves performance as opposed to if we just had one dataframe. Separating by context also makes it much easier to parse the fields we have access to in Tableau, so in general our Python work pays dividends here. The visualizations are separated into 5 dashboards, and a top frame that is shared across all dashboards that contains total respondent count, respondent counts by year, buttons to access the dashboards and filters for survey year, coding experience and professional coding experience. To keep the visualizations clean, responses that do not include any meaningful data in terms of visualizations created here (like respondents that claim to not use ANY coding language at work despite identifying as developers) are excluded from the tracked counts, but not from the '% of total' values. The 5 dashboards are as follows:

  - **Overview** dashboard, which stores all the contextual filters and charts from the other pages and a brief description of how the dashboards are formatted.
![Overview](https://github.com/user-attachments/assets/e493b76d-80f0-4df7-a0be-a6d49bb5ac2f)

  - **Demographics** dashboard, which includes visualizations for respondents by country and average compensation by age, as well as charts and contextual filters for respondent count by age group and employment status
![Demographics](https://github.com/user-attachments/assets/7540ad16-cc68-43d9-9a3b-5493456cf58d)

  - **Career** dashboard, which includes visualizations for respondent count by organization size and remote/in-person work, compensation by seniority at work and top 10 developer types by compensation, as well as a chart and contextual filter for respondent count by developer type
![Career](https://github.com/user-attachments/assets/eac25e7a-6098-4193-8c80-ff6a07fc8d2a)

  - **Education** dashboard, which includes visualizations for compensation by education level and online learning methods' popularity by age groups, as well as charts and contextual filters for respondent count by education level and learning activity
![Education](https://github.com/user-attachments/assets/6af42d6f-a20e-486b-9364-bb5f1c722f12)

  - **Tech** dashboard, which includes visualizations for top 10 coding languages and databases by usage and demand, and charts and contextual filters for used and desired languages and databases
![Tech](https://github.com/user-attachments/assets/e9255d36-e1d2-4bf8-b2aa-1b516574ab1a)


  
