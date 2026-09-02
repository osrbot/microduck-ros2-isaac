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
    { text: 'Start here', link: '/guide/' },
    { text: 'ROS 2', link: '/ros2/' },
    { text: 'Isaac Sim', link: '/isaac/' },
    {
      text: 'Help',
      items: [
        { text: 'Troubleshooting', link: '/troubleshooting' },
        { text: 'Frequently asked questions', link: '/faq' },
        { text: 'Tested setup', link: '/reference/environment' },
        { text: 'Known limitations', link: '/reference/limitations' }
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
          { text: 'Choose a tutorial', link: '/guide/' },
          { text: 'Installation', link: '/guide/installation' }
        ]
      }
    ],
    '/ros2/': [
      {
        text: 'ROS 2 tutorial',
        items: [
          { text: 'Open MicroDuck in RViz', link: '/ros2/' },
          { text: 'RViz controls and joints', link: '/ros2/rviz' },
          { text: 'Run the ROS 2 examples', link: '/ros2/examples' },
          { text: 'Drive Isaac from ROS 2', link: '/ros2/isaac-control' }
        ]
      }
    ],
    '/isaac/': [
      {
        text: 'Isaac Sim tutorial',
        items: [
          { text: 'Open MicroDuck in Isaac Sim', link: '/isaac/' },
          { text: 'Run one policy', link: '/isaac/policy-playback' },
          { text: 'Open the skill playground', link: '/isaac/playground' },
          { text: 'Train a walking policy', link: '/isaac/training' },
          { text: 'Build another task', link: '/isaac/custom-environment' }
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
    quote: 'The duck is here. This page waddled off.',
    linkLabel: 'Go to the documentation home',
    linkText: 'Back to home'
  },
  footer: {
    message: 'Independent community project. Not affiliated with or endorsed by Pollen Robotics.',
    copyright: 'Original integration code is licensed under Apache-2.0.'
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
    { text: '从这里开始', link: '/zh/guide/' },
    { text: 'ROS 2 教程', link: '/zh/ros2/' },
    { text: 'Isaac Sim 教程', link: '/zh/isaac/' },
    {
      text: '遇到问题',
      items: [
        { text: '故障排查', link: '/zh/troubleshooting' },
        { text: '常见问题', link: '/zh/faq' },
        { text: '测试环境', link: '/zh/reference/environment' },
        { text: '已知限制', link: '/zh/reference/limitations' }
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
          { text: '今天怎么遛鸭？', link: '/zh/guide/' },
          { text: '安装需要的软件', link: '/zh/guide/installation' }
        ]
      }
    ],
    '/zh/ros2/': [
      {
        text: 'ROS 2 教程',
        items: [
          { text: '把鸭子请进 RViz', link: '/zh/ros2/' },
          { text: '转转镜头，活动关节', link: '/zh/ros2/rviz' },
          { text: '跑几个 ROS 2 例程', link: '/zh/ros2/examples' },
          { text: '用 ROS 2 遥控 Isaac', link: '/zh/ros2/isaac-control' }
        ]
      }
    ],
    '/zh/isaac/': [
      {
        text: 'Isaac Sim 教程',
        items: [
          { text: '把鸭子放进 Isaac Sim', link: '/zh/isaac/' },
          { text: '先放一只鸭开跑', link: '/zh/isaac/policy-playback' },
          { text: '打开多动作游乐场', link: '/zh/isaac/playground' },
          { text: '训练一只会走的鸭', link: '/zh/isaac/training' },
          { text: '自己再造一个训练任务', link: '/zh/isaac/custom-environment' }
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
    quote: '鸭子还在，这一页跑丢了。',
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
    'A step-by-step ROS 2 and NVIDIA Isaac Sim tutorial for MicroDuck.',
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
          'Open MicroDuck in RViz, move its joints, and run the walking policy in Isaac Sim.'
      }
    ],
    ['meta', { name: 'twitter:card', content: 'summary_large_image' }],
    ['meta', { name: 'twitter:title', content: 'MicroDuck ROS 2 + Isaac Sim' }],
    [
      'meta',
      {
        name: 'twitter:description',
        content: 'A practical ROS 2 and Isaac Sim tutorial for MicroDuck.'
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
        'A step-by-step ROS 2 and NVIDIA Isaac Sim tutorial for MicroDuck.',
      themeConfig: englishTheme
    },
    zh: {
      label: '简体中文',
      lang: 'zh-CN',
      link: '/zh/',
      title: 'MicroDuck ROS 2 + Isaac Sim',
      description: '一步一步把 MicroDuck 放进 ROS 2 和 NVIDIA Isaac Sim。',
      themeConfig: chineseTheme
    }
  },
  themeConfig: englishTheme
})
