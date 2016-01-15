module.exports = (grunt) ->
  grunt.loadNpmTasks 'grunt-contrib-watch'
  grunt.loadNpmTasks 'grunt-contrib-coffee'
  grunt.loadNpmTasks 'grunt-browserify'

  grunt.registerTask 'default', ['coffee', 'browserify', 'watch']

  grunt.initConfig
    coffee:
      compile:
        expand: true,
        flatten: false,
        cwd: "src/",
        src: ['**/*.coffee'],
        dest: 'compiled/',
        ext: '.js'
    browserify:
      main:
        src: 'compiled/main.js'
        dest: 'bin/game.js'
    watch:
      files: 'src/**/*.coffee'
      tasks: ['coffee', 'browserify']

  undefined