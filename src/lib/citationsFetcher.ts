import { getConfig } from './config';

interface CitationData {
  schemaVersion: number;
  label: string;
  message: string;
}

interface GSData {
  publications?: Record<string, {
    bib?: {
      title?: string;
    };
    num_citations?: number;
  }>;
}

// Cache for citation data to avoid repeated API calls
let citationsCache: Map<string, number> | null = null;
let cacheTimestamp: number = 0;
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

/**
 * Normalize title for matching (same logic as in Python crawler)
 */
function normalizeTitle(title: string): string {
  return title.replace(/\W+/g, '').toLowerCase();
}

/**
 * Fetch a file from GitHub repository using raw content URL
 */
async function fetchGitHubFile(
  repo: string,
  branch: string,
  filePath: string
): Promise<string | null> {
  // Use raw.githubusercontent.com for direct file access
  const url = `https://raw.githubusercontent.com/${repo}/${branch}/${filePath}`;
  
  try {
    const response = await fetch(url, {
      headers: {
        'Accept': 'application/vnd.github.v3.raw',
      },
      next: { revalidate: 300 }, // Cache for 5 minutes
    });

    if (!response.ok) {
      if (response.status === 404) {
        console.warn(`File not found: ${url}`);
        return null;
      }
      throw new Error(`GitHub API error: ${response.status}`);
    }

    return await response.text();
  } catch (error) {
    console.error(`Error fetching ${url}:`, error);
    return null;
  }
}

/**
 * List files in a GitHub directory using GitHub API
 */
async function listGitHubDirectory(
  repo: string,
  branch: string,
  dirPath: string
): Promise<string[]> {
  const url = `https://api.github.com/repos/${repo}/contents/${dirPath}?ref=${branch}`;
  
  try {
    const response = await fetch(url, {
      headers: {
        'Accept': 'application/vnd.github.v3+json',
      },
      next: { revalidate: 300 },
    });

    if (!response.ok) {
      if (response.status === 404) {
        console.warn(`Directory not found: ${dirPath}`);
        return [];
      }
      throw new Error(`GitHub API error: ${response.status}`);
    }

    const files = await response.json();
    return files
      .filter((f: { type: string; name: string }) => f.type === 'file' && f.name.endsWith('.json'))
      .map((f: { name: string }) => f.name);
  } catch (error) {
    console.error(`Error listing directory ${dirPath}:`, error);
    return [];
  }
}

/**
 * Parse individual paper citation file (paper_YYYY_title.json format)
 */
function parsePaperCitationFile(
  filename: string,
  content: string
): { normalizedTitle: string; citations: number } | null {
  try {
    const data: CitationData = JSON.parse(content);
    
    // Extract title from filename: paper_YYYY_titlepart.json
    const match = filename.match(/^paper_\d{4}_(.+)\.json$/);
    if (!match) return null;
    
    const normalizedTitle = match[1];
    const citations = parseInt(data.message) || 0;
    
    return { normalizedTitle, citations };
  } catch {
    return null;
  }
}

/**
 * Fetch and parse gs_data.json for comprehensive citation matching
 */
async function fetchGSData(
  repo: string,
  branch: string,
  dataPath: string
): Promise<GSData | null> {
  // Handle different path formats:
  // - Empty path: gs_data.json is at root
  // - Path ending with gs_data.json: use as-is
  // - Directory path: append gs_data.json
  let filePath: string;
  if (!dataPath || dataPath === '') {
    filePath = 'gs_data.json';
  } else if (dataPath.endsWith('gs_data.json')) {
    filePath = dataPath;
  } else {
    filePath = `${dataPath}/gs_data.json`;
  }
  
  const content = await fetchGitHubFile(repo, branch, filePath);
  if (!content) return null;
  
  try {
    return JSON.parse(content);
  } catch {
    console.error('Error parsing gs_data.json');
    return null;
  }
}

/**
 * Build citation map from gs_data.json
 */
function buildCitationMapFromGSData(gsData: GSData): Map<string, number> {
  const citationMap = new Map<string, number>();
  
  if (!gsData.publications) return citationMap;
  
  for (const pub of Object.values(gsData.publications)) {
    const title = pub.bib?.title;
    if (title) {
      const normalizedTitle = normalizeTitle(title);
      const citations = pub.num_citations || 0;
      citationMap.set(normalizedTitle, citations);
    }
  }
  
  return citationMap;
}

/**
 * Build citation map from individual paper JSON files
 */
async function buildCitationMapFromFiles(
  repo: string,
  branch: string,
  dataPath: string
): Promise<Map<string, number>> {
  const citationMap = new Map<string, number>();
  
  // List all files in the results directory
  const files = await listGitHubDirectory(repo, branch, dataPath);
  
  // Filter for paper citation files
  const paperFiles = files.filter(f => f.startsWith('paper_'));
  
  // Fetch all paper files in parallel
  const fetchPromises = paperFiles.map(async (filename) => {
    const content = await fetchGitHubFile(repo, branch, `${dataPath}/${filename}`);
    if (content) {
      const result = parsePaperCitationFile(filename, content);
      if (result) {
        citationMap.set(result.normalizedTitle, result.citations);
      }
    }
  });
  
  await Promise.all(fetchPromises);
  
  return citationMap;
}

/**
 * Get citations for all papers from GitHub repository
 * Returns a Map with normalized title as key and citation count as value
 */
export async function fetchCitationsFromGitHub(): Promise<Map<string, number>> {
  const config = getConfig();
  const citationsConfig = config.citations;
  
  // Check if citations config is properly set
  if (!citationsConfig?.github_repo) {
    console.log('No GitHub repo configured for citations');
    return new Map();
  }
  
  const repo = citationsConfig.github_repo;
  const branch = citationsConfig.github_branch || 'main';
  const dataPath = citationsConfig.data_path;
  
  // Check cache
  const now = Date.now();
  if (citationsCache && (now - cacheTimestamp) < CACHE_DURATION) {
    return citationsCache;
  }
  
  console.log(`Fetching citations from GitHub: ${repo}/${branch}/${dataPath}`);
  
  // First try to get gs_data.json for comprehensive data
  const gsData = await fetchGSData(repo, branch, dataPath);
  
  let citationMap: Map<string, number>;
  
  if (gsData && gsData.publications) {
    // Use gs_data.json as primary source
    citationMap = buildCitationMapFromGSData(gsData);
    console.log(`Loaded ${citationMap.size} citations from gs_data.json`);
  } else {
    // Fall back to individual paper files
    citationMap = await buildCitationMapFromFiles(repo, branch, dataPath);
    console.log(`Loaded ${citationMap.size} citations from individual files`);
  }
  
  // Update cache
  citationsCache = citationMap;
  cacheTimestamp = now;
  
  return citationMap;
}

/**
 * Get citation count for a specific paper by title
 */
export function getCitationCount(
  citationMap: Map<string, number>,
  title: string
): number {
  const normalizedTitle = normalizeTitle(title);
  
  // Try exact match first
  if (citationMap.has(normalizedTitle)) {
    return citationMap.get(normalizedTitle)!;
  }
  
  // Try partial match
  for (const [key, value] of citationMap.entries()) {
    // Check if one title contains the other
    if (normalizedTitle.includes(key) || key.includes(normalizedTitle)) {
      return value;
    }
    
    // Check first 30 characters match (same as Python crawler)
    if (key.length >= 30 && normalizedTitle.startsWith(key.substring(0, 30))) {
      return value;
    }
    if (normalizedTitle.length >= 30 && key.startsWith(normalizedTitle.substring(0, 30))) {
      return value;
    }
  }
  
  return 0;
}

/**
 * Clear the citation cache (useful for testing or forcing refresh)
 */
export function clearCitationCache(): void {
  citationsCache = null;
  cacheTimestamp = 0;
}
