import requests

query = '''
query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {
  problemsetQuestionList: questionList(
    categorySlug: $categorySlug
    limit: $limit
    skip: $skip
    filters: $filters
  ) {
    total: totalNum
    questions: data {
      acRate
      difficulty
      freqBar
      frontendQuestionId: questionFrontendId
      isFavor
      paidOnly: isPaidOnly
      status
      title
      titleSlug
      topicTags {
        name
        id
        slug
      }
      hasSolution
      hasVideoSolution
    }
  }
}
'''
variables = {'categorySlug': '', 'skip': 0, 'limit': 2, 'filters': {}}
try:
    resp = requests.post('https://leetcode.com/graphql', json={'query': query, 'variables': variables})
    print(resp.status_code)
    print(resp.json())
except Exception as e:
    print(e)
