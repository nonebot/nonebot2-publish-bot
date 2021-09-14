import * as core from '@actions/core'
import * as github from '@actions/github'
import {
  checkLabel,
  extractInfo,
  extractIssueNumberFromRef,
  publishComment
} from './utils'
import {OctokitType} from './types/github'
import {PluginInfo} from './types/plugin'
import {BotInfo} from './types/bot'
import {AdapterInfo} from './types/adapter'

export async function check(octokit: OctokitType): Promise<void> {
  // 只处理支持标签的拉取请求
  const issueType = checkLabel(github.context.payload.pull_request?.labels)
  if (issueType) {
    const ref: string = github.context.payload.pull_request?.head.ref
    const issue_number = extractIssueNumberFromRef(ref)
    if (!issue_number) {
      core.setFailed('无法获取议题')
      return
    }
    const issue = await octokit.issues.get({
      ...github.context.repo,
      issue_number
    })
    const info = extractInfo(
      issueType,
      issue.data.body ?? '',
      issue.data.user?.login ?? ''
    )
    // 不同类型有不同类型的检查方法
    switch (info.type) {
      case 'Bot':
        checkBot(octokit, info)
        break
      case 'Adapter':
        checkAdapter(octokit, info)
        break
      case 'Plugin':
        checkPlugin(octokit, info, issue_number)
        break
    }
  } else {
    core.info('拉取请求与插件无关，已跳过')
  }
}

async function checkPlugin(
  octokit: OctokitType,
  info: PluginInfo,
  issue_number: number
): Promise<void> {
  core.info(`插件 ${info.name}`)
  await publishComment(octokit, issue_number, `插件 ${info.name} 没有问题`)
}
async function checkBot(octokit: OctokitType, info: BotInfo): Promise<void> {
  core.info(`机器人 ${info.name}`)
}
async function checkAdapter(
  octokit: OctokitType,
  info: AdapterInfo
): Promise<void> {
  core.info(`适配器 ${info.name}`)
}
