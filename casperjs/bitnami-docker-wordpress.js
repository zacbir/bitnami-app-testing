'use strict';

//casper.options.waitTimeout = 10000;
//casper.options.pageSettings.resourceTimeout = 10000;

casper.on('started', function() { this.page.customHeaders = {'Accept-Language': 'en-us'}; });

casper.test.begin('add posts test', function (test) {
  var _this = this;
  casper.start('http://{{HOSTNAME}}/');
  casper.waitForSelector('a[href*="wp-login.php"]', function () {
    test.assertExists('a[href*="wp-login.php"]', 'Login button exists');
    this.click('a[href*="wp-login.php"]');
  });
  casper.waitForSelector('input#user_login', function () {
    test.assertExists('input#user_login', 'Reached login screen');
    this.sendKeys('input#user_login', 'user');
    this.sendKeys('input#user_pass', 'bitnami');
    this.click('input#wp-submit');
  });
  casper.thenOpen('http://{{HOSTNAME}}/wp-admin/edit.php');
  casper.waitForSelector('li.publish', function () {
    test.assertExists('li.publish', 'Reached Posts screen');
  });
  casper.waitForSelector('a[class*="page-title-action"]', function () {
    test.assertExists('a[class*="page-title-action"]', 'Add New Post button exists');
    this.click('a[class*="page-title-action"]');
  });
  casper.waitForSelector('body', function () {
    test.assertTitleMatch(/.*Add New (Post|Page).*/, 'Inside creation page');
    this.sendKeys('form#post input#title', 'Test post');
  });
  casper.then(function () {
    this.page.switchToChildFrame(0);
  });
  casper.waitForSelector('body#tinymce', function () {
    test.assertExists('body#tinymce', 'Content input exists');
    this.sendKeys('body#tinymce', 'Body content');
  });
  casper.then(function () {
    casper.page.switchToParentFrame();
  });
  casper.waitForSelector('form input[name="publish"]:not([class*="disabled"])', function () {
    test.assertExists('form input[name="publish"]:not([class*="disabled"])', 'Publish button exists');
    this.click('form input[name="publish"]:not([class*="disabled"])');
  });
  casper.run(function () {
    test.done();
  });
});
