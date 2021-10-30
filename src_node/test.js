const cardano = require('cardano-api')

const address = 'DdzFFzCqrht8iQ2utWYssBnfGvSqkGfM7fxHXZWoB57ormT17td1CY4Eye7bADF6HpeGC57vwV5ZPzmVjiZRQEkAD9Rc4P8LDF7FfYne'

// promise
cardano.address({address})
  .then(data => console.log('promise', data))
  .catch(err => console.log('err', err))

// async/await
const myCardanoFunc = async address => {
  try {
    const data = await cardano.address(address)
    console.log('async/await', data)
  }
  catch(err) { console.log(err) }
}

myCardanoFunc({address})
