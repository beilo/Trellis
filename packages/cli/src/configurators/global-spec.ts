/**
 * 全局 spec 部署 — 将 global-spec/ 模板部署到 ~/.trellis/spec/
 *
 * 路径: ~/.trellis/spec/ 是跨项目通用的机器级规则目录。
 * 结构: backend/, frontend/, guides/ 三个子目录，与模板源一致。
 * 幂等: init 时直接覆盖写入；update 时保留用户修改过的文件。
 */

import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import { getGlobalSpecFiles } from "../templates/global-spec/index.js";

/** 全局 spec 的目标目录 */
const GLOBAL_SPEC_DIR = path.join(os.homedir(), ".trellis", "spec");

/**
 * 部署全局 spec 到 ~/.trellis/spec/
 * init 模式: 直接写入所有模板文件，确保目录和文件存在。
 */
export async function deployGlobalSpec(): Promise<void> {
  const files = getGlobalSpecFiles();

  for (const [relativePath, content] of files) {
    const targetPath = path.join(GLOBAL_SPEC_DIR, relativePath);
    const dir = path.dirname(targetPath);

    // 确保目录存在
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }

    // 写入文件（init 覆盖写）
    fs.writeFileSync(targetPath, content, "utf-8");
  }
}

/**
 * 同步全局 spec: 仅更新用户未修改的文件，保留用户定制。
 * 判断依据: 文件存在且内容与模板一致 → 更新；文件存在但内容不同 → 跳过；文件不存在 → 写入。
 * update 模式使用。
 */
export async function syncGlobalSpec(): Promise<{
  updated: string[];
  skipped: string[];
  created: string[];
}> {
  const files = getGlobalSpecFiles();
  const updated: string[] = [];
  const skipped: string[] = [];
  const created: string[] = [];

  for (const [relativePath, content] of files) {
    const targetPath = path.join(GLOBAL_SPEC_DIR, relativePath);
    const dir = path.dirname(targetPath);

    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }

    if (!fs.existsSync(targetPath)) {
      // 文件不存在 → 写入
      fs.writeFileSync(targetPath, content, "utf-8");
      created.push(relativePath);
    } else {
      const existing = fs.readFileSync(targetPath, "utf-8");
      if (existing === content) {
        // 内容一致，不需要更新
        continue;
      }
      // 内容不同 → 跳过（保留用户修改）
      skipped.push(relativePath);
    }
  }

  return { updated, skipped, created };
}
