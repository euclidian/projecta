module.exports = function(grunt) {

    // Project configuration.
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),

        // Task configuration goes here.
        concat: {
            changes: {
                src: ['changes/static/js/*.js'],
                dest: '../static/js/changes.js'
            }
        },

        uglify: {
          changes: {
              files: {
                '../static/js/changes.min.js': ['changes/static/js/*.js']
              }
          }
        }
    });

    // Load plugins here.
    grunt.loadNpmTasks('grunt-contrib-concat');
    grunt.loadNpmTasks('grunt-contrib-uglify');

    // Register tasks here.
    grunt.registerTask('default', ['uglify']);
};
