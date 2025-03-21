package cat

import "fmt"

// 대문자 : public export, 소문자 : private
type Cat struct {
	name string
	age  int
}

// receiver function
func (c Cat) SetDetails(name string, age int) {
	c.name = name
	c.age = age
	fmt.Println("SeeDetails blue: ", c)
}

// receiver pointer function
func (c *Cat) RealSetDetails(name string, age int) {
	c.name = name
	c.age = age
	fmt.Println("RealSetDetails blue: ", c)
}
