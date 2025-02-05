package main

import (
	"fmt"

	"github.com/amamov/sangcoin/helloGo/cat"
)

func plus(a ...int) int {
	var total int
	for _, item := range a {
		total += item
	}

	return total

}

func multiple(a int, b int, hello string) (int, string) {
	return a * b, hello
}

type person struct {
	name string
	age  int
}

// recevier func
func (p person) sayHello() {
	fmt.Printf("Hello! My name is %s and I'm %d\n", p.name, p.age)
}

func main() {
	name := "sang" // var name string = "sang"
	name = "hello world"
	fmt.Println(name)
	fmt.Println(plus(1, 2, 3, 4))
	fmt.Println(multiple(2, 3, "hello"))

	for index, letter := range name {
		fmt.Println(index, string(letter))
	}

	x := 123478173249
	fmt.Printf("%b\n", x)
	xAsBinary := fmt.Sprintf("%b\n ", x)
	fmt.Println(xAsBinary)

	foods := [3]string{"potato", "pizza", "pasta"} // array
	// foods := []string{"potato", "pizza", "pasta"} --> slice (array 크기 무한)
	for _, dish := range foods {
		fmt.Println(dish)
	}

	for i := 0; i < len(foods); i++ {
		fmt.Println(foods[i])
	}

	coins := []string{"BTC", "XRP", "ETH", "SUI"} // slice
	fmt.Printf("%v\n", coins)
	coins = append(coins, "SANG")
	fmt.Printf("%v\n", coins)

	a := 2
	b := a
	a = 12
	fmt.Println(b)
	fmt.Println(&a, &b) // address

	// pointer
	c := 2
	d := &c
	c = 12
	fmt.Println(&c, d, *d)

	sang := person{age: 28, name: "sangseok"} // person{"sangseok", 28}

	fmt.Println(sang.name, sang.age)
	sang.sayHello()

	blue := cat.Cat{}
	blue.SetDetails("blue", 3)
	fmt.Println("Main blue", blue) // Main blue { 0} --> SetDetails의 c는 복사본이기에 blue 자체를 바꾸지 않음

	blue.RealSetDetails("blue", 3)
	fmt.Println("Main blue", blue) // Main blue {blue 3}
}
