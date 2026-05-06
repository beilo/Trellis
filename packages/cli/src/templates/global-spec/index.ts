/**
 * 全局 spec 模板
 *
 * 目录结构:
 *   global-spec/
 *   ├── backend/      # 后端规范 (7 文件)
 *   ├── frontend/     # 前端规范 (7 文件)
 *   └── guides/       # 思维指南 (6 文件)
 */

import { createTemplateReader } from "../template-utils.js";

const { readTemplate, listFiles } = createTemplateReader(import.meta.url);

/** 全局 spec 的子目录列表 */
const SPEC_DIRS = ["backend", "frontend", "guides"];

/**
 * 获取所有全局 spec 文件内容
 * 返回 Map<相对路径, 文件内容>，键如 "backend/index.md"
 */
export const getGlobalSpecFiles = (): Map<string, string> => {
  const files = new Map<string, string>();

  for (const dir of SPEC_DIRS) {
    const entries = listFiles(dir)
      .filter((f) => f.endsWith(".md"))
      .sort();

    for (const filename of entries) {
      const relativePath = `${dir}/${filename}`;
      files.set(relativePath, readTemplate(relativePath));
    }
  }

  return files;
};
