import { defineConfig, type DefaultTheme } from 'vitepress'

const repository = 'https://github.com/osrbot/microduck-ros2-isaac'

const search: DefaultTheme.Config['search'] = {
  provider: 'local',
  options: {
    detailedView: true,
    locales: {
      zh: {
        translations: {
          button: {
            buttonText: '搜索文档',
            buttonAriaLabel: '搜索文档'
          },
          modal: {
            displayDetails: '显示详细列表',
            resetButtonTitle: '清除查询',
            backButtonTitle: '关闭搜索',
            noResultsText: '没有找到相关结果',
            footer: {
              selectText: '选择',
              navigateText: '切换',
              closeText: '关闭'
            }
          }
        }
      }
    }
  }
}

const helpSidebar: DefaultTheme.SidebarItem[] = [
  {
    text: 'Help',
    items: [
      { text: 'Troubleshooting', link: '/troubleshooting' },
      { text: 'Frequently asked questions', link: '/faq' },
      { text: 'Known limitations', link: '/reference/limitations' }
    ]
  }
]

const englishTheme: DefaultTheme.Config = {
  siteTitle: 'MicroDuck ROS 2 + Isaac',
  externalLinkIcon: true,
  search,
  socialLinks: [{ icon: 'github', link: repository }],
  nav: [
    { text: 'Start', link: '/guide/' },
    { text: 'ROS 2', link: '/ros2/' },
    { text: 'Isaac Sim', link: '/isaac/' },
    {
      text: 'Reference',
      items: [
        { text: 'Architecture', link: '/concepts/architecture' },
        { text: 'Validation', link: '/reference/validation' },
        { text: 'Results', link: '/reference/results' },
        { text: 'Troubleshooting', link: '/troubleshooting' }
      ]
    }
  ],
  sidebar: {
    '/troubleshooting': helpSidebar,
    '/faq': helpSidebar,
    '/guide/': [
      {
        text: 'Start here',
        items: [
          { text: 'Choose a path', link: '/guide/' },
          { text: 'Install and prepare', link: '/guide/installation' }
        ]
      }
    ],
    '/ros2/': [
      {
        text: 'ROS 2 and RViz',
        items: [
          { text: 'Build the description', link: '/ros2/' },
          { text: 'Use RViz', link: '/ros2/rviz' }
        ]
      }
    ],
    '/isaac/': [
      {
        text: 'Isaac Sim',
        items: [
          { text: 'Create and inspect USD', link: '/isaac/' },
          { text: 'Replay ONNX policies', link: '/isaac/policy-playback' }
        ]
      }
    ],
    '/concepts/': [
      {
        text: 'Concepts',
        items: [{ text: 'Architecture', link: '/concepts/architecture' }]
      }
    ],
    '/reference/': [
      {
        text: 'Reference',
        items: [
          { text: 'Validated environment', link: '/reference/environment' },
          { text: 'Validation model', link: '/reference/validation' },
          { text: 'Recorded results', link: '/reference/results' },
          { text: 'Known limitations', link: '/reference/limitations' }
        ]
      }
    ],
    '/project/': [
      {
        text: 'Project',
        items: [
          { text: 'Licensing', link: '/project/licensing' },
          { text: 'Livestream guide', link: '/project/livestream' },
          { text: 'Contributing', link: '/project/contributing' }
        ]
      }
    ]
  },
  outline: { level: [2, 3], label: 'On this page' },
  docFooter: { prev: 'Previous', next: 'Next' },
  darkModeSwitchLabel: 'Appearance',
  sidebarMenuLabel: 'Menu',
  returnToTopLabel: 'Return to top',
  langMenuLabel: 'Change language',
  notFound: {
    title: 'Page not found',
    quote: 'The model is pinned. This URL is not.',
    linkLabel: 'Go to the documentation home',
    linkText: 'Back to home'
  },
  footer: {
    message: 'Independent community project. Not affiliated with or endorsed by Pollen Robotics.',
    copyright: 'Original integration code licensed under Apache-2.0.'
  }
}

const chineseHelpSidebar: DefaultTheme.SidebarItem[] = [
  {
    text: '帮助',
    items: [
      { text: '故障排查', link: '/zh/troubleshooting' },
      { text: '常见问题', link: '/zh/faq' },
      { text: '已知限制', link: '/zh/reference/limitations' }
    ]
  }
]

const chineseTheme: DefaultTheme.Config = {
  siteTitle: 'MicroDuck ROS 2 + Isaac',
  externalLinkIcon: true,
  search,
  socialLinks: [{ icon: 'github', link: repository }],
  nav: [
    { text: '入门', link: '/zh/guide/' },
    { text: 'ROS 2', link: '/zh/ros2/' },
    { text: 'Isaac Sim', link: '/zh/isaac/' },
    {
      text: '参考',
      items: [
        { text: '架构', link: '/zh/concepts/architecture' },
        { text: '验证体系', link: '/zh/reference/validation' },
        { text: '验证结果', link: '/zh/reference/results' },
        { text: '故障排查', link: '/zh/troubleshooting' }
      ]
    }
  ],
  sidebar: {
    '/zh/troubleshooting': chineseHelpSidebar,
    '/zh/faq': chineseHelpSidebar,
    '/zh/guide/': [
      {
        text: '从这里开始',
        items: [
          { text: '选择路线', link: '/zh/guide/' },
          { text: '安装与准备', link: '/zh/guide/installation' }
        ]
      }
    ],
    '/zh/ros2/': [
      {
        text: 'ROS 2 与 RViz',
        items: [
          { text: '构建机器人描述', link: '/zh/ros2/' },
          { text: '使用 RViz', link: '/zh/ros2/rviz' }
        ]
      }
    ],
    '/zh/isaac/': [
      {
        text: 'Isaac Sim',
        items: [
          { text: '生成并检查 USD', link: '/zh/isaac/' },
          { text: '回放 ONNX 策略', link: '/zh/isaac/policy-playback' }
        ]
      }
    ],
    '/zh/concepts/': [
      {
        text: '概念',
        items: [{ text: '项目架构', link: '/zh/concepts/architecture' }]
      }
    ],
    '/zh/reference/': [
      {
        text: '参考资料',
        items: [
          { text: '已验证环境', link: '/zh/reference/environment' },
          { text: '验证体系', link: '/zh/reference/validation' },
          { text: '验证结果', link: '/zh/reference/results' },
          { text: '已知限制', link: '/zh/reference/limitations' }
        ]
      }
    ],
    '/zh/project/': [
      {
        text: '项目',
        items: [
          { text: '许可与发布边界', link: '/zh/project/licensing' },
          { text: '直播演示指南', link: '/zh/project/livestream' },
          { text: '参与贡献', link: '/zh/project/contributing' }
        ]
      }
    ]
  },
  outline: { level: [2, 3], label: '本页内容' },
  docFooter: { prev: '上一页', next: '下一页' },
  darkModeSwitchLabel: '外观',
  sidebarMenuLabel: '目录',
  returnToTopLabel: '回到顶部',
  langMenuLabel: '切换语言',
  notFound: {
    title: '页面不存在',
    quote: '模型版本固定了，但这个地址没有。',
    linkLabel: '返回文档首页',
    linkText: '返回首页'
  },
  footer: {
    message: '独立社区项目，与 Pollen Robotics 不存在隶属或背书关系。',
    copyright: '原创兼容代码采用 Apache-2.0 许可。'
  }
}

export default defineConfig({
  title: 'MicroDuck ROS 2 + Isaac Sim',
  description:
    'An independent ROS 2 Jazzy and NVIDIA Isaac Sim integration for Pollen Robotics MicroDuck.',
  base: '/microduck-ros2-isaac/',
  cleanUrls: true,
  appearance: true,
  lastUpdated: false,
  sitemap: {
    hostname: 'https://osrbot.github.io/microduck-ros2-isaac/'
  },
  head: [
    ['link', { rel: 'icon', type: 'image/svg+xml', href: '/microduck-ros2-isaac/favicon.svg' }],
    ['meta', { name: 'theme-color', content: '#faf8f2' }],
    ['meta', { name: 'author', content: 'OSRBOT community' }],
    ['meta', { property: 'og:type', content: 'website' }],
    ['meta', { property: 'og:site_name', content: 'MicroDuck ROS 2 + Isaac Sim' }],
    ['meta', { property: 'og:title', content: 'MicroDuck ROS 2 + Isaac Sim' }],
    ['meta', { property: 'og:url', content: 'https://osrbot.github.io/microduck-ros2-isaac/' }],
    [
      'meta',
      {
        property: 'og:image',
        content: 'https://osrbot.github.io/microduck-ros2-isaac/og.png'
      }
    ],
    [
      'meta',
      {
        property: 'og:description',
        content:
          'ROS 2 visualization, validated USD assets, and released ONNX policy playback for MicroDuck.'
      }
    ],
    ['meta', { name: 'twitter:card', content: 'summary_large_image' }],
    ['meta', { name: 'twitter:title', content: 'MicroDuck ROS 2 + Isaac Sim' }],
    [
      'meta',
      {
        name: 'twitter:description',
        content: 'ROS 2 visualization, validated USD assets, and ONNX policy playback.'
      }
    ],
    [
      'meta',
      {
        name: 'twitter:image',
        content: 'https://osrbot.github.io/microduck-ros2-isaac/og.png'
      }
    ]
  ],
  locales: {
    root: {
      label: 'English',
      lang: 'en-US',
      title: 'MicroDuck ROS 2 + Isaac Sim',
      description:
        'An independent ROS 2 Jazzy and NVIDIA Isaac Sim integration for Pollen Robotics MicroDuck.',
      themeConfig: englishTheme
    },
    zh: {
      label: '简体中文',
      lang: 'zh-CN',
      link: '/zh/',
      title: 'MicroDuck ROS 2 + Isaac Sim',
      description: '面向 Pollen Robotics MicroDuck 的独立 ROS 2 Jazzy 与 NVIDIA Isaac Sim 兼容项目。',
      themeConfig: chineseTheme
    }
  },
  themeConfig: englishTheme
})
