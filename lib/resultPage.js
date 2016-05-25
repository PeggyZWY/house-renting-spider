window.onload = function() {
  var trList = document.getElementsByTagName("tr"),
      trListLength = trList.length;

  // 为表内容里的偶数行添加类名，以显示斑马线似的表格
  for (var i = 1; i < trListLength; i++) {
    if (i % 2 === 0) {
      trList[i].className = "even";
    }
  }


  var thList = document.getElementsByTagName("th"),
      thListLength = thList.length;

  // 为表头添加类名，以在媒体查询是隐藏相关的元素
  for (var i = 0; i < thListLength; i++) {
    if (i < 2) {
      j = i;
    } else {
      j = i + 1;
    }
    thList[i].className = "column" + j;
  }
}