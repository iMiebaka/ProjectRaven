const options_one = {
  method: "GET",
  // body: JSON.stringify(data_field),
  headers: {
    Accept: "application/json",
    "Content-Type": "application/json",
    "X-CSRFToken": csrf_token,
  },
};



fetch(stripe_config, options_one)
  .then((result) => {
    return result.json();
  })
  .then((data) => {
    // Initialize Stripe.js
    const stripe = Stripe(data.publicKey);
    document
      .querySelector("#strip_btn")
      .addEventListener("click", () => {
        // Get Checkout Session ID
        const options_two = {
          method: "POST",
          body: JSON.stringify({ 'purchase_option': purchase_option }),
          headers: {
            Accept: "application/json",
            "Content-Type": "application/json",
            "X-CSRFToken": csrf_token,
          },
        };
        console.log(purchase_option);
        document.querySelector("#strip_btn").setAttribute('disabled', 'disabled')
        setTimeout(function (){
          document.querySelector("#strip_btn").removeAttribute('disabled')
        }, 120000)

        stripe_purchase_option = fetch(create_checkout_session, options_two)
        .then((result) => {
          return result.json();
        })
        .then((data) => {
          // Redirect to Stripe Checkout
          return stripe.redirectToCheckout({ sessionId: data.sessionId });
          document.querySelector("#strip_btn").removeAttribute('disabled')
          })
          .then((res) => {
            console.log(res);
          document.querySelector("#strip_btn").removeAttribute('disabled')
          });
      });
  });

// console.log("Sanity check!");
