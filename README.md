# AI STOCK UPDATES
#### Video Demo:  <URL HERE>
#### Description: A personal news feed for listed companies, summarized by AI

## Intro
I built an app that let's you follow stock traded companies and have a personal feed with news updates summarized with Gemeni's LLM. As an investor myself, I really wanted to built something, that I might use myself, or something that I could built upon in the future. I started out with the idea to have AI generated summaries of quarterly reports in your mailbox. The idea morphed and became something quite different along the way. I had some problems for instance with what data could be reliably called upon through an external API. I couldn't find a (free) api that allowed me to access the latest reports, so I pivotted into summarizing news.

## Building the project
I started by watching how to built a flask application from scratch to get a refresher on how flask works, since it had been a while since I finished week 9. I then took the Finance app and used that as the basis for my project, since the idea has a lot of overlap. You can still see the remnants of Finance when you create a user and forget to enter a password for instance, this will lead you to the apology page. I deleted or changed what I didn't need and started the project from there.

### Database
I setup a database for users and subscriptions that I had to change a couple of times, to include for instance the cashed versions of news summaries to improve loading time. Switching what you are trying to built mid-flight can be tricky, but in this case I only had to add a couple of columns, rather the reorganize the whole database.

### API's
I've tried a couple of API's and even had multiple ones at one time, before finding Finnhub. I use it to:

1. To generate a list of companies that exist and can be searched. This list is loaded when the dashboard loads, so search is quite quick.
2. To get a list of news articles, (limited to 10) for each company that a user follows.

I then use the Gemini api to create a summary of all the news. I ran into the problem that while building I was quickly running into api call limits and loading time was exploding. I decided to cache these summaries in the database, and only going back to pull news when the summary exceeds a certain age, in this case 1 hour.

### Structure, JS and CSS
I've used a very similar structure as the Finance app, with a single database file, app.py, helpers.py, templates containing the html, and some static files containing one javascript file for the dashboard and some styles. I only use javascript in the search function, when looking for companies to follow. It creates an overlay of possible matches in the database. For the design, I'm mainly using Bootstrap, and some custom css for displaying the search results and stock ticker. It all makes use of the same styles.css file Finance uses.

### Setting boundaries
Once I was building I found I quickly generated more ideas for improvement that I didn't really need. For instance I built a live stock ticker at the top of the page, like you see in many finance apps. The original idea of providing email updates never made it into the final project, for now. I hope to built upon this project in the future and adress some of the performance issues for instance that still exist, because generating one summary takes quite some time.

### Use of LLM's
As a user of Google's Gemini I used it's 2.5 pro model to guide me through the process of building an application from scratch. I was quite amazed how much I was able to achieve in a relatively short period of time, when the answers you are looking for ar often just a few seconds away. I tried to keep the LLM's from doing to much of the heavy lifting by setting up it's role as a coach and helping me learn rather then giving me answers. I explained that the project was the final project for CS50 and what my experience was. It is hard to keep yourself from using the LLM for everything and not lean on it too much, I guess this is a grey area. When it did generated code that I used, I asked it to explain things or go over each line to learn from it rather then copying and pasting. Literlary typing the code, even though it takes longer, helps you to stay disciplined in that way. Even when setting the context in this way, the LLM's really try to help you as best as they can, even generating code when you don't ask for it, so it's quite tricky.
What was really nice and really improved my efficiency is that it helpt me organize my thoughts a lot. I explained what I wanted to do and it created a todo list to guide me. It also was useful in reminiding me where I was after a few days off. To make it much easier to pick up where I left off.


## Conclusion
I really feel that a whole world is opening up by finishing this project. It is amazing that we live in a time where our abilities can be amplified by using AI. I know that this would have taken me much longer, or would have turned out so nice if I would have to use stackoverflow. I've been learning programming for years off and on and it's hard when you do it on the side. For me this project feels like an important step from tutorial hell to independence.
