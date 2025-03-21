package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
)

const port string = ":5000"

type URLDescription struct {
	URL         string `json:"url"`
	Method      string `json:"method"`
	Description string `json:"description`
}

func documentation(rw http.ResponseWriter, r *http.Request) {
	data := []URLDescription{
		{
			URL:         "/",
			Method:      "GET",
			Description: "See Documentaion",
		},
	}
	rw.Header().Add("Content-Type", "application/json")
	json.NewEncoder(rw).Encode(data)

}

func main() {

	// frontend.Start()
	http.HandleFunc("/", documentation)
	fmt.Printf("Listening on http://localhost%s", port)
	log.Fatal(http.ListenAndServe(port, nil))
}
