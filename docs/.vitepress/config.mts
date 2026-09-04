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
      { text: 'FAQ', link: '/faq' }
    ]
  }
]

const englishTutorialSidebar: DefaultTheme.SidebarItem[] = [
  {
    text: 'Start',
    items: [
      { text: '1. Pick a route', link: '/guide/' },
      { text: '2. Check your computer', link: '/guide/installation' }
    ]
  },
  {
    text: 'ROS 2',
    items: [
      { text: '3. Open MicroDuck in RViz', link: '/ros2/' },
      { text: '4. Move the camera and joints', link: '/ros2/rviz' },
      { text: '5. Try the ROS 2 examples', link: '/ros2/examples' }
    ]
  },
  {
    text: 'Isaac Sim',
    items: [
      { text: '6. Open MicroDuck in Isaac Sim', link: '/isaac/' },
      { text: '7. Make the duck walk', link: '/isaac/policy-playback' },
      { text: '8. Play with the moves', link: '/isaac/playground' }
    ]
  },
  {
    text: 'Go further',
    items: [
      { text: '9. Connect ROS 2 and Isaac', link: '/ros2/isaac-control' },
      { text: '10. Train a walking policy', link: '/isaac/training' }
    ]
  },
  {
    text: 'Case study: continuous rolling',
    items: [
      { text: '11. Watch the result and start training', link: '/isaac/continuous-roll' },
      { text: '12. Parameters and rewards', link: '/isaac/roll-parameters' },
      { text: '13. Three rounds of debugging', link: '/isaac/roll-debugging' },
      { text: '14. Evaluate and export video', link: '/isaac/roll-validation' },
      { text: '15. Make a new training task', link: '/isaac/custom-environment' }
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
    { text: 'Requirements', link: '/guide/installation' },
    { text: 'ROS 2', link: '/ros2/' },
    { text: 'Isaac Sim', link: '/isaac/' },
    {
      text: 'Help',
      items: [
        { text: 'Troubleshooting', link: '/troubleshooting' },
        { text: 'FAQ', link: '/faq' }
      ]
    }
  ],
  sidebar: {
    '/troubleshooting': helpSidebar,
    '/faq': helpSidebar,
    '/guide/': englishTutorialSidebar,
    '/ros2/': englishTutorialSidebar,
    '/isaac/': englishTutorialSidebar,
    '/concepts/': [
      {
        text: 'Concepts',
        items: [{ text: 'Architecture', link: '/concepts/architecture' }]
      }
    ],
    '/reference/': [
      {
        text: 'Contributor notes',
        items: [
          { text: 'Tested setup', link: '/reference/environment' },
          { text: 'How this project was tested', link: '/reference/validation' },
          { text: 'Saved test results', link: '/reference/results' },
          { text: 'Technical limits', link: '/reference/limitations' }
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
    message: 'Open-source tutorial by OSRBOT × GPUS.',
    copyright: 'Original integration code is licensed under Apache-2.0.'
  }
}

const chineseHelpSidebar: DefaultTheme.SidebarItem[] = [
  {
    text: '帮助',
    items: [
      { text: '故障排查', link: '/zh/troubleshooting' },
      { text: '常见问题', link: '/zh/faq' }
    ]
  }
]

const chineseTutorialSidebar: DefaultTheme.SidebarItem[] = [
  {
    text: '先准备好',
    items: [
      { text: '1. 先选一条路线', link: '/zh/guide/' },
      { text: '2. 看电脑能不能跑', link: '/zh/guide/installation' }
    ]
  },
  {
    text: '先玩 ROS 2',
    items: [
      { text: '3. 把鸭子请进 RViz', link: '/zh/ros2/' },
      { text: '4. 转镜头、动关节', link: '/zh/ros2/rviz' },
      { text: '5. 跑几个 ROS 2 例程', link: '/zh/ros2/examples' }
    ]
  },
  {
    text: '再去 Isaac Sim',
    items: [
      { text: '6. 打开 MicroDuck 模型', link: '/zh/isaac/' },
      { text: '7. 先让鸭子走起来', link: '/zh/isaac/policy-playback' },
      { text: '8. 玩多动作游乐场', link: '/zh/isaac/playground' }
    ]
  },
  {
    text: '继续折腾',
    items: [
      { text: '9. 用 ROS 2 控制 Isaac', link: '/zh/ros2/isaac-control' },
      { text: '10. 训练一只会走的鸭', link: '/zh/isaac/training' }
    ]
  },
  {
    text: '实战：连续翻滚',
    items: [
      { text: '11. 先看效果，再开始训练', link: '/zh/isaac/continuous-roll' },
      { text: '12. 参数和奖励怎么设计', link: '/zh/isaac/roll-parameters' },
      { text: '13. 三轮调试复盘', link: '/zh/isaac/roll-debugging' },
      { text: '14. 验收模型，导出素材', link: '/zh/isaac/roll-validation' },
      { text: '15. 自己做一个训练任务', link: '/zh/isaac/custom-environment' }
    ]
  }
]

const chineseTheme: DefaultTheme.Config = {
  siteTitle: 'MicroDuck ROS 2 + Isaac',
  externalLinkIcon: true,
  search,
  socialLinks: [{ icon: 'github', link: repository }],
  nav: [
    { text: '开始玩鸭', link: '/zh/guide/' },
    { text: '环境要求', link: '/zh/guide/installation' },
    { text: 'ROS 2', link: '/zh/ros2/' },
    { text: 'Isaac Sim', link: '/zh/isaac/' },
    {
      text: '遇到问题',
      items: [
        { text: '故障排查', link: '/zh/troubleshooting' },
        { text: '常见问题', link: '/zh/faq' }
      ]
    }
  ],
  sidebar: {
    '/zh/troubleshooting': chineseHelpSidebar,
    '/zh/faq': chineseHelpSidebar,
    '/zh/guide/': chineseTutorialSidebar,
    '/zh/ros2/': chineseTutorialSidebar,
    '/zh/isaac/': chineseTutorialSidebar,
    '/zh/concepts/': [
      {
        text: '概念',
        items: [{ text: '项目架构', link: '/zh/concepts/architecture' }]
      }
    ],
    '/zh/reference/': [
      {
        text: '维护者资料',
        items: [
          { text: '测试过的环境', link: '/zh/reference/environment' },
          { text: '这个项目怎么测试', link: '/zh/reference/validation' },
          { text: '保留的测试记录', link: '/zh/reference/results' },
          { text: '技术边界', link: '/zh/reference/limitations' }
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
    message: 'OSRBOT × GPUS 开源技术教程。',
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
