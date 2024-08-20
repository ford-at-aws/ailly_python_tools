# Ailly Python Tools
[Ailly](https://github.com/davidsouther/ailly) is a tool that allows you to interact easily with LLM's in an iterative and autonomous way. 

The Ailly primitives (see CLI) lack a few features, so the projects in this repository are Python wrappers that show how to use Ailly to peform common user tasks.

| project       | dir                              | purpose                                       |
|---------------|----------------------------------|-----------------------------------------------|
| uxr_analysis  | [/uxr_analysis](/uxr_analysis)   | Summarizes and scores UX research videos.     |
| code-reviewer | [/code-reviewer](/code-reviewer) | Reviews code bases using provided standards.  |
| pr-reviewer   | [/pr-reviewer](/pr-reviewer)     | Reviews GitHub PR's using provided standards. |

# Cost warning
Note that these scripts interact with AWS, which costs money. Proceed with caution in this regard and track usage using [best practices](https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-best-practices.html).
