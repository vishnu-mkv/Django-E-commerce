// $(document).on("click", ".Id_submit", function (event) {
//   event.preventDefault();
//   var selector = $(this).closest(".productID");
//   console.log(selector.find("form").attr("action"));
//   const form_data = {
//     csrfmiddlewaretoken: $(
//       '#transactionIDValue input[name="csrfmiddlewaretoken"]'
//     ).val(),
//   };

//   $.ajax({
//     type: "POST",
//     url: selector.find("form").attr("action"),
//     data: form_data,
//     success: function () {
//       alert("Product added to cart");
//     },
//   });
// });

async function POSTData(api, data) {
  const response = await fetch(api, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });
  res = await response.json();
  if (res.redirect) {
    window.location.href = res.redirect;
  }
  return res;
}

async function addToCart(e, id, quantity = 1, uiUpdate = true) {
  response = await POSTData("/cart/add", {
    product_id: id,
    quantity: quantity,
  });
  if (response["success"] && uiUpdate) {
    e?.target.classList.add("d-none");
    e.target.previousElementSibling?.classList.remove("d-none");
  }
  // log(response);
  if (response["success"]) {
    return true;
  }
  return false;
}

async function removeFromCart(e, id, del = false) {
  response = await POSTData("/cart/remove", {
    product_id: id,
  });

  if (response["success"]) {
    e.target.classList?.add("d-none");
    e.target.nextElementSibling?.classList.remove("d-none");
    console.log(del);
    if (del) {
      location.reload();
    }
  }
}

async function updateCount(e, id, count) {
  let res = await addToCart(e, id, count, false);
  // reload page
  location.reload();
  return res;
}

async function update(e, id) {
  const count = parseInt(e.target.value);
  if (count < 1) {
    e.target.value = 1;
    return;
  }
  if (count > parseInt($(e.target).attr("max"))) {
    e.target.value = $(e.target).attr("max");
    return;
  }
  let res = await updateCount(e, id, count);
}

// increment
async function incrementCount(e, id) {
  const ele = $(e.target).parent().parent().find(".counter");
  const count = ele.val();
  console.log(count);
  let res = await updateCount(e, id, parseInt(count) + 1);
  if (res) {
    ele.val(parseInt(count) + 1);
  }
}

// decrement
async function decrementCount(e, id) {
  const ele = $(e.target).parent().parent().find(".counter");
  const count = ele.val();
  if (parseInt(count) > 1) {
    let res = await updateCount(e, id, parseInt(count) - 1);
    if (res) {
      ele.val(parseInt(count) - 1);
    }
  }
}
